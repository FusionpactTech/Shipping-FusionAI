"""
Rate Limiting and Caching Module

This module provides comprehensive rate limiting and caching features for enterprise
deployments, including configurable request throttling, quota management, and
intelligent caching strategies.

Author: Fusionpact Technologies Inc.
Date: 2025-01-18
Version: 1.0.0
"""

import time
import hashlib
import json
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
import logging
import asyncio
from collections import defaultdict, deque

import redis.asyncio as aioredis
from fastapi import HTTPException, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .config import config, RateLimitConfig, CacheConfig
from .tenancy import get_current_tenant_id, get_current_tenant


class RateLimitStrategy(str, Enum):
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"


class CacheStrategy(str, Enum):
    LRU = "lru"
    LFU = "lfu"
    TTL = "ttl"
    ADAPTIVE = "adaptive"


class RateLimitRule:
    """Rate limiting rule configuration."""
    
    def __init__(self, requests: int, window: int, strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW):
        self.requests = requests
        self.window = window  # in seconds
        self.strategy = strategy
        self.created_at = datetime.utcnow()


class CacheEntry:
    """Cache entry with metadata."""
    
    def __init__(self, key: str, value: Any, ttl: int = 3600):
        self.key = key
        self.value = value
        self.created_at = datetime.utcnow()
        self.last_accessed = datetime.utcnow()
        self.access_count = 0
        self.ttl = ttl
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return datetime.utcnow() > self.created_at + timedelta(seconds=self.ttl)
    
    def access(self) -> None:
        """Mark entry as accessed."""
        self.last_accessed = datetime.utcnow()
        self.access_count += 1


class RateLimiter:
    """Advanced rate limiter with multiple strategies."""
    
    def __init__(self):
        self.rules: Dict[str, RateLimitRule] = {}
        self.counters: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.logger = logging.getLogger(__name__)
        self._load_default_rules()
    
    def _load_default_rules(self) -> None:
        """Load default rate limiting rules."""
        settings = RateLimitConfig.get_rate_limit_settings()
        
        # Global rate limits
        self.add_rule("global", RateLimitRule(
            requests=settings["requests"],
            window=settings["window"],
            strategy=RateLimitStrategy.SLIDING_WINDOW
        ))
        
        # Per-endpoint rate limits
        self.add_rule("process_documents", RateLimitRule(
            requests=50,
            window=3600,
            strategy=RateLimitStrategy.SLIDING_WINDOW
        ))
        
        self.add_rule("analytics", RateLimitRule(
            requests=100,
            window=3600,
            strategy=RateLimitStrategy.SLIDING_WINDOW
        ))
        
        self.add_rule("api_requests", RateLimitRule(
            requests=1000,
            window=3600,
            strategy=RateLimitStrategy.SLIDING_WINDOW
        ))
    
    def add_rule(self, name: str, rule: RateLimitRule) -> None:
        """Add a rate limiting rule."""
        self.rules[name] = rule
    
    def check_rate_limit(self, identifier: str, rule_name: str = "global") -> Tuple[bool, Dict[str, Any]]:
        """Check if rate limit is exceeded."""
        if not RateLimitConfig.is_rate_limiting_enabled():
            return True, {}
        
        rule = self.rules.get(rule_name)
        if not rule:
            return True, {}
        
        counter_key = f"{rule_name}:{identifier}"
        current_time = time.time()
        
        if rule.strategy == RateLimitStrategy.SLIDING_WINDOW:
            return self._check_sliding_window(counter_key, rule, current_time)
        elif rule.strategy == RateLimitStrategy.FIXED_WINDOW:
            return self._check_fixed_window(counter_key, rule, current_time)
        elif rule.strategy == RateLimitStrategy.TOKEN_BUCKET:
            return self._check_token_bucket(counter_key, rule, current_time)
        else:
            return True, {}
    
    def _check_sliding_window(self, counter_key: str, rule: RateLimitRule, current_time: float) -> Tuple[bool, Dict[str, Any]]:
        """Check rate limit using sliding window strategy."""
        window_start = current_time - rule.window
        
        # Get current requests in window
        requests = self.counters[counter_key].get("requests", [])
        
        # Remove expired requests
        requests = [req for req in requests if req > window_start]
        
        # Check if limit exceeded
        if len(requests) >= rule.requests:
            return False, {
                "limit": rule.requests,
                "remaining": 0,
                "reset_time": min(requests) + rule.window,
                "window": rule.window
            }
        
        # Add current request
        requests.append(current_time)
        self.counters[counter_key]["requests"] = requests
        
        return True, {
            "limit": rule.requests,
            "remaining": rule.requests - len(requests),
            "reset_time": current_time + rule.window,
            "window": rule.window
        }
    
    def _check_fixed_window(self, counter_key: str, rule: RateLimitRule, current_time: float) -> Tuple[bool, Dict[str, Any]]:
        """Check rate limit using fixed window strategy."""
        window_start = int(current_time // rule.window) * rule.window
        
        counter = self.counters[counter_key]
        current_window = counter.get("window", 0)
        current_count = counter.get("count", 0)
        
        if current_window != window_start:
            # New window, reset counter
            counter["window"] = window_start
            counter["count"] = 1
            return True, {
                "limit": rule.requests,
                "remaining": rule.requests - 1,
                "reset_time": window_start + rule.window,
                "window": rule.window
            }
        else:
            # Same window, increment counter
            if current_count >= rule.requests:
                return False, {
                    "limit": rule.requests,
                    "remaining": 0,
                    "reset_time": window_start + rule.window,
                    "window": rule.window
                }
            
            counter["count"] = current_count + 1
            return True, {
                "limit": rule.requests,
                "remaining": rule.requests - counter["count"],
                "reset_time": window_start + rule.window,
                "window": rule.window
            }
    
    def _check_token_bucket(self, counter_key: str, rule: RateLimitRule, current_time: float) -> Tuple[bool, Dict[str, Any]]:
        """Check rate limit using token bucket strategy."""
        counter = self.counters[counter_key]
        last_refill = counter.get("last_refill", current_time)
        tokens = counter.get("tokens", rule.requests)
        
        # Calculate tokens to add
        time_passed = current_time - last_refill
        tokens_to_add = (time_passed / rule.window) * rule.requests
        tokens = min(rule.requests, tokens + tokens_to_add)
        
        if tokens < 1:
            return False, {
                "limit": rule.requests,
                "remaining": 0,
                "reset_time": last_refill + rule.window,
                "window": rule.window
            }
        
        # Consume token
        tokens -= 1
        counter["tokens"] = tokens
        counter["last_refill"] = current_time
        
        return True, {
            "limit": rule.requests,
            "remaining": int(tokens),
            "reset_time": current_time + rule.window,
            "window": rule.window
        }


class CacheManager:
    """Advanced cache manager with multiple strategies."""
    
    def __init__(self):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = 1000
        self.strategy = CacheStrategy.LRU
        self.logger = logging.getLogger(__name__)
        self._redis_client: Optional[aioredis.Redis] = None
        self._init_redis()
    
    def _init_redis(self) -> None:
        """Initialize Redis connection if enabled."""
        if CacheConfig.is_cache_enabled():
            try:
                self._redis_client = aioredis.from_url(
                    CacheConfig.get_redis_url(),
                    encoding="utf-8",
                    decode_responses=True
                )
                self.logger.info("Redis cache initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Redis: {e}")
                self._redis_client = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not CacheConfig.is_cache_enabled():
            return None
        
        # Try Redis first
        if self._redis_client:
            try:
                value = await self._redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                self.logger.warning(f"Redis get failed: {e}")
        
        # Fallback to memory cache
        entry = self.cache.get(key)
        if entry and not entry.is_expired():
            entry.access()
            return entry.value
        
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        if not CacheConfig.is_cache_enabled():
            return
        
        ttl = ttl or CacheConfig.get_cache_ttl()
        
        # Try Redis first
        if self._redis_client:
            try:
                await self._redis_client.setex(
                    key,
                    ttl,
                    json.dumps(value)
                )
                return
            except Exception as e:
                self.logger.warning(f"Redis set failed: {e}")
        
        # Fallback to memory cache
        entry = CacheEntry(key, value, ttl)
        
        # Evict if cache is full
        if len(self.cache) >= self.max_size:
            self._evict_entry()
        
        self.cache[key] = entry
    
    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        if not CacheConfig.is_cache_enabled():
            return
        
        # Try Redis first
        if self._redis_client:
            try:
                await self._redis_client.delete(key)
                return
            except Exception as e:
                self.logger.warning(f"Redis delete failed: {e}")
        
        # Fallback to memory cache
        if key in self.cache:
            del self.cache[key]
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        if not CacheConfig.is_cache_enabled():
            return
        
        # Try Redis first
        if self._redis_client:
            try:
                await self._redis_client.flushdb()
                return
            except Exception as e:
                self.logger.warning(f"Redis clear failed: {e}")
        
        # Fallback to memory cache
        self.cache.clear()
    
    def _evict_entry(self) -> None:
        """Evict an entry based on cache strategy."""
        if not self.cache:
            return
        
        if self.strategy == CacheStrategy.LRU:
            # Remove least recently used
            lru_key = min(self.cache.keys(), key=lambda k: self.cache[k].last_accessed)
            del self.cache[lru_key]
        elif self.strategy == CacheStrategy.LFU:
            # Remove least frequently used
            lfu_key = min(self.cache.keys(), key=lambda k: self.cache[k].access_count)
            del self.cache[lfu_key]
        elif self.strategy == CacheStrategy.TTL:
            # Remove expired entries first, then oldest
            expired_keys = [k for k, v in self.cache.items() if v.is_expired()]
            if expired_keys:
                del self.cache[expired_keys[0]]
            else:
                oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k].created_at)
                del self.cache[oldest_key]


class QuotaManager:
    """Manages usage quotas and limits."""
    
    def __init__(self):
        self.quotas: Dict[str, Dict[str, Any]] = {}
        self.usage: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.logger = logging.getLogger(__name__)
        self._load_default_quotas()
    
    def _load_default_quotas(self) -> None:
        """Load default quota configurations."""
        self.quotas = {
            "documents_per_day": {
                "limit": 10000,
                "window": 86400,  # 24 hours
                "reset_time": "daily"
            },
            "api_requests_per_hour": {
                "limit": 1000,
                "window": 3600,  # 1 hour
                "reset_time": "hourly"
            },
            "storage_gb": {
                "limit": 100,
                "window": None,  # No time window
                "reset_time": "manual"
            },
            "concurrent_requests": {
                "limit": 50,
                "window": None,  # No time window
                "reset_time": "manual"
            }
        }
    
    def check_quota(self, tenant_id: str, quota_type: str, amount: int = 1) -> Tuple[bool, Dict[str, Any]]:
        """Check if quota is exceeded."""
        quota = self.quotas.get(quota_type)
        if not quota:
            return True, {}
        
        current_usage = self.usage[tenant_id][quota_type]
        
        if current_usage + amount > quota["limit"]:
            return False, {
                "quota_type": quota_type,
                "limit": quota["limit"],
                "current_usage": current_usage,
                "requested": amount,
                "remaining": max(0, quota["limit"] - current_usage)
            }
        
        return True, {
            "quota_type": quota_type,
            "limit": quota["limit"],
            "current_usage": current_usage,
            "requested": amount,
            "remaining": quota["limit"] - (current_usage + amount)
        }
    
    def increment_usage(self, tenant_id: str, quota_type: str, amount: int = 1) -> None:
        """Increment usage for quota type."""
        self.usage[tenant_id][quota_type] += amount
        self.logger.info(f"Incremented {quota_type} usage for tenant {tenant_id}: +{amount}")
    
    def reset_usage(self, tenant_id: str, quota_type: str) -> None:
        """Reset usage for quota type."""
        self.usage[tenant_id][quota_type] = 0
        self.logger.info(f"Reset {quota_type} usage for tenant {tenant_id}")
    
    def get_usage_summary(self, tenant_id: str) -> Dict[str, Any]:
        """Get usage summary for tenant."""
        summary = {}
        for quota_type, quota in self.quotas.items():
            current_usage = self.usage[tenant_id][quota_type]
            summary[quota_type] = {
                "limit": quota["limit"],
                "current_usage": current_usage,
                "remaining": max(0, quota["limit"] - current_usage),
                "percentage": (current_usage / quota["limit"]) * 100 if quota["limit"] > 0 else 0
            }
        return summary


class RateLimitMiddleware:
    """FastAPI middleware for rate limiting."""
    
    def __init__(self, rate_limiter: RateLimiter, quota_manager: QuotaManager):
        self.rate_limiter = rate_limiter
        self.quota_manager = quota_manager
        self.logger = logging.getLogger(__name__)
    
    async def __call__(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Get tenant ID
        tenant_id = get_current_tenant_id() or "default"
        
        # Get client identifier
        client_id = self._get_client_identifier(request)
        
        # Check rate limits
        allowed, rate_limit_info = self.rate_limiter.check_rate_limit(
            f"{tenant_id}:{client_id}",
            "api_requests"
        )
        
        if not allowed:
            self.logger.warning(f"Rate limit exceeded for {client_id}")
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded",
                headers={
                    "X-RateLimit-Limit": str(rate_limit_info["limit"]),
                    "X-RateLimit-Remaining": str(rate_limit_info["remaining"]),
                    "X-RateLimit-Reset": str(int(rate_limit_info["reset_time"]))
                }
            )
        
        # Check quotas
        allowed, quota_info = self.quota_manager.check_quota(tenant_id, "api_requests_per_hour")
        
        if not allowed:
            self.logger.warning(f"Quota exceeded for tenant {tenant_id}")
            raise HTTPException(
                status_code=429,
                detail="Quota exceeded",
                headers={
                    "X-Quota-Limit": str(quota_info["limit"]),
                    "X-Quota-Remaining": str(quota_info["remaining"])
                }
            )
        
        # Increment usage
        self.quota_manager.increment_usage(tenant_id, "api_requests_per_hour")
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(rate_limit_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(rate_limit_info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(int(rate_limit_info["reset_time"]))
        
        return response
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Try to get from headers
        client_id = request.headers.get("X-Client-ID")
        if client_id:
            return client_id
        
        # Use IP address as fallback
        client_ip = request.client.host if request.client else "unknown"
        return client_ip


# Global instances
rate_limiter = RateLimiter()
cache_manager = CacheManager()
quota_manager = QuotaManager()
rate_limit_middleware = RateLimitMiddleware(rate_limiter, quota_manager)


def get_cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments."""
    key_parts = [str(arg) for arg in args]
    key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
    return hashlib.md5(":".join(key_parts).encode()).hexdigest()


async def cached_result(ttl: int = 3600):
    """Decorator for caching function results."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = get_cache_key(func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_value = await cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            await cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator
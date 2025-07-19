"""
Enterprise Rate Limiting Module

This module provides comprehensive rate limiting capabilities for the vessel
maintenance AI system, including configurable request throttling, quota
management, and production-ready rate limiting strategies.

Author: Fusionpact Technologies Inc.
Date: 2025-01-27
Version: 2.0.0
License: MIT License
"""

import time
import hashlib
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from fastapi import HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
import redis
import json
import asyncio
from dataclasses import dataclass
import structlog

from .config import settings
from .tenant import TenantContext

logger = structlog.get_logger(__name__)


@dataclass
class RateLimitRule:
    """Rate limit rule configuration"""
    requests: int  # Number of requests allowed
    window: int    # Time window in seconds
    per: str      # Per what (ip, user, tenant, endpoint)
    burst: int = 0  # Additional burst allowance


class RateLimitInfo(BaseModel):
    """Rate limit information for response headers"""
    limit: int
    remaining: int
    reset: int
    retry_after: Optional[int] = None


class RateLimitConfig(BaseModel):
    """Rate limit configuration model"""
    enabled: bool = True
    rules: List[RateLimitRule] = Field(default_factory=list)
    default_limits: Dict[str, RateLimitRule] = Field(default_factory=dict)
    exempt_ips: List[str] = Field(default_factory=list)
    exempt_users: List[str] = Field(default_factory=list)
    custom_responses: Dict[str, str] = Field(default_factory=dict)


class RateLimitStorage:
    """Abstract base class for rate limit storage backends"""
    
    async def get_count(self, key: str, window: int) -> int:
        """Get current request count for key within window"""
        raise NotImplementedError
    
    async def increment(self, key: str, window: int, expire: int) -> int:
        """Increment request count and return new count"""
        raise NotImplementedError
    
    async def get_reset_time(self, key: str, window: int) -> int:
        """Get timestamp when the rate limit resets"""
        raise NotImplementedError
    
    async def clear_key(self, key: str):
        """Clear rate limit data for key"""
        raise NotImplementedError


class MemoryRateLimitStorage(RateLimitStorage):
    """In-memory rate limit storage (for development/testing)"""
    
    def __init__(self):
        self._storage: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
    
    async def get_count(self, key: str, window: int) -> int:
        """Get current request count for key within window"""
        async with self._lock:
            now = time.time()
            if key not in self._storage:
                return 0
            
            data = self._storage[key]
            
            # Clean old entries
            data["requests"] = [
                req_time for req_time in data["requests"]
                if now - req_time < window
            ]
            
            return len(data["requests"])
    
    async def increment(self, key: str, window: int, expire: int) -> int:
        """Increment request count and return new count"""
        async with self._lock:
            now = time.time()
            
            if key not in self._storage:
                self._storage[key] = {
                    "requests": [],
                    "created": now
                }
            
            data = self._storage[key]
            
            # Clean old entries
            data["requests"] = [
                req_time for req_time in data["requests"]
                if now - req_time < window
            ]
            
            # Add current request
            data["requests"].append(now)
            
            return len(data["requests"])
    
    async def get_reset_time(self, key: str, window: int) -> int:
        """Get timestamp when the rate limit resets"""
        async with self._lock:
            if key not in self._storage:
                return int(time.time() + window)
            
            data = self._storage[key]
            if not data["requests"]:
                return int(time.time() + window)
            
            oldest_request = min(data["requests"])
            return int(oldest_request + window)
    
    async def clear_key(self, key: str):
        """Clear rate limit data for key"""
        async with self._lock:
            if key in self._storage:
                del self._storage[key]


class RedisRateLimitStorage(RateLimitStorage):
    """Redis-based rate limit storage (for production)"""
    
    def __init__(self, redis_url: str = None, redis_password: str = None):
        self.redis_url = redis_url or settings.redis_url
        self.redis_password = redis_password or settings.redis_password
        self._redis = None
    
    def _get_redis(self) -> redis.Redis:
        """Get Redis connection"""
        if self._redis is None:
            self._redis = redis.from_url(
                self.redis_url,
                password=self.redis_password,
                decode_responses=True
            )
        return self._redis
    
    async def get_count(self, key: str, window: int) -> int:
        """Get current request count for key within window"""
        r = self._get_redis()
        now = time.time()
        cutoff = now - window
        
        # Remove old entries and count remaining
        pipe = r.pipeline()
        pipe.zremrangebyscore(key, 0, cutoff)
        pipe.zcard(key)
        results = pipe.execute()
        
        return results[1]
    
    async def increment(self, key: str, window: int, expire: int) -> int:
        """Increment request count and return new count"""
        r = self._get_redis()
        now = time.time()
        cutoff = now - window
        
        pipe = r.pipeline()
        
        # Remove old entries
        pipe.zremrangebyscore(key, 0, cutoff)
        
        # Add current request
        pipe.zadd(key, {str(now): now})
        
        # Set expiration
        pipe.expire(key, expire)
        
        # Count requests in window
        pipe.zcard(key)
        
        results = pipe.execute()
        return results[3]  # Count result
    
    async def get_reset_time(self, key: str, window: int) -> int:
        """Get timestamp when the rate limit resets"""
        r = self._get_redis()
        
        # Get oldest request in current window
        oldest = r.zrange(key, 0, 0, withscores=True)
        
        if not oldest:
            return int(time.time() + window)
        
        oldest_time = oldest[0][1]
        return int(oldest_time + window)
    
    async def clear_key(self, key: str):
        """Clear rate limit data for key"""
        r = self._get_redis()
        r.delete(key)


class RateLimiter:
    """
    Enterprise-grade rate limiter with configurable rules and storage backends.
    
    This class provides comprehensive rate limiting functionality including
    per-IP, per-user, per-tenant, and per-endpoint rate limiting with
    configurable storage backends and custom response handling.
    """
    
    def __init__(self, storage: Optional[RateLimitStorage] = None):
        if storage is None:
            if settings.cache_backend.value == "redis":
                self.storage = RedisRateLimitStorage()
            else:
                self.storage = MemoryRateLimitStorage()
        else:
            self.storage = storage
        
        self.config = self._load_config()
    
    def _load_config(self) -> RateLimitConfig:
        """Load rate limiting configuration"""
        default_rules = []
        
        if settings.rate_limiting_enabled:
            # Default rate limit rules based on settings
            default_rules = [
                RateLimitRule(
                    requests=settings.rate_limit_per_minute,
                    window=60,
                    per="ip",
                    burst=settings.rate_limit_burst
                ),
                RateLimitRule(
                    requests=settings.rate_limit_per_hour,
                    window=3600,
                    per="ip"
                ),
                RateLimitRule(
                    requests=settings.rate_limit_per_day,
                    window=86400,
                    per="ip"
                )
            ]
        
        return RateLimitConfig(
            enabled=settings.rate_limiting_enabled,
            rules=default_rules
        )
    
    async def check_rate_limit(
        self,
        request: Request,
        identifier: Optional[str] = None,
        endpoint: Optional[str] = None
    ) -> Tuple[bool, RateLimitInfo]:
        """
        Check if request should be rate limited.
        
        Args:
            request: FastAPI request object
            identifier: Custom identifier (user_id, tenant_id, etc.)
            endpoint: Specific endpoint being accessed
            
        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        if not self.config.enabled:
            return True, RateLimitInfo(limit=0, remaining=0, reset=0)
        
        # Extract identifiers
        ip_address = self._get_client_ip(request)
        user_id = getattr(request.state, "user_id", None)
        tenant_id = getattr(request.state, "tenant_id", None)
        
        # Check exemptions
        if self._is_exempt(ip_address, user_id):
            return True, RateLimitInfo(limit=0, remaining=0, reset=0)
        
        # Get applicable rules
        applicable_rules = self._get_applicable_rules(
            ip_address, user_id, tenant_id, endpoint
        )
        
        # Check each rule
        most_restrictive_info = None
        
        for rule in applicable_rules:
            key = self._generate_key(rule, ip_address, user_id, tenant_id, endpoint)
            
            # Get current count
            current_count = await self.storage.get_count(key, rule.window)
            
            # Calculate remaining requests
            effective_limit = rule.requests + rule.burst
            remaining = max(0, effective_limit - current_count)
            
            # Get reset time
            reset_time = await self.storage.get_reset_time(key, rule.window)
            
            rate_info = RateLimitInfo(
                limit=effective_limit,
                remaining=remaining,
                reset=reset_time
            )
            
            # Check if limit exceeded
            if current_count >= effective_limit:
                rate_info.retry_after = reset_time - int(time.time())
                return False, rate_info
            
            # Track most restrictive rule
            if most_restrictive_info is None or remaining < most_restrictive_info.remaining:
                most_restrictive_info = rate_info
        
        return True, most_restrictive_info or RateLimitInfo(limit=0, remaining=0, reset=0)
    
    async def record_request(
        self,
        request: Request,
        identifier: Optional[str] = None,
        endpoint: Optional[str] = None
    ):
        """
        Record a request for rate limiting purposes.
        
        Args:
            request: FastAPI request object
            identifier: Custom identifier
            endpoint: Specific endpoint being accessed
        """
        if not self.config.enabled:
            return
        
        # Extract identifiers
        ip_address = self._get_client_ip(request)
        user_id = getattr(request.state, "user_id", None)
        tenant_id = getattr(request.state, "tenant_id", None)
        
        # Get applicable rules
        applicable_rules = self._get_applicable_rules(
            ip_address, user_id, tenant_id, endpoint
        )
        
        # Record request for each rule
        for rule in applicable_rules:
            key = self._generate_key(rule, ip_address, user_id, tenant_id, endpoint)
            await self.storage.increment(key, rule.window, rule.window * 2)
    
    def _get_applicable_rules(
        self,
        ip_address: str,
        user_id: Optional[str],
        tenant_id: Optional[str],
        endpoint: Optional[str]
    ) -> List[RateLimitRule]:
        """Get rate limit rules applicable to the current request"""
        applicable_rules = []
        
        # Add default rules
        applicable_rules.extend(self.config.rules)
        
        # Add tenant-specific rules if available
        if tenant_id:
            tenant = TenantContext.get_current_tenant()
            if tenant and hasattr(tenant, "rate_limit_rules"):
                applicable_rules.extend(tenant.rate_limit_rules)
        
        # Add endpoint-specific rules
        if endpoint and endpoint in self.config.default_limits:
            applicable_rules.append(self.config.default_limits[endpoint])
        
        return applicable_rules
    
    def _generate_key(
        self,
        rule: RateLimitRule,
        ip_address: str,
        user_id: Optional[str],
        tenant_id: Optional[str],
        endpoint: Optional[str]
    ) -> str:
        """Generate rate limit key for storage"""
        parts = ["rate_limit", rule.per]
        
        if rule.per == "ip":
            parts.append(ip_address)
        elif rule.per == "user" and user_id:
            parts.append(user_id)
        elif rule.per == "tenant" and tenant_id:
            parts.append(tenant_id)
        elif rule.per == "endpoint" and endpoint:
            parts.append(endpoint)
        else:
            # Fallback to IP-based limiting
            parts = ["rate_limit", "ip", ip_address]
        
        # Add window to make keys unique per time window
        parts.append(str(rule.window))
        
        key = ":".join(parts)
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded IP (behind proxy)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        return getattr(request.client, "host", "unknown")
    
    def _is_exempt(self, ip_address: str, user_id: Optional[str]) -> bool:
        """Check if request is exempt from rate limiting"""
        # Check IP exemptions
        if ip_address in self.config.exempt_ips:
            return True
        
        # Check user exemptions
        if user_id and user_id in self.config.exempt_users:
            return True
        
        return False
    
    def add_rule(self, rule: RateLimitRule):
        """Add a new rate limiting rule"""
        self.config.rules.append(rule)
    
    def remove_rule(self, rule: RateLimitRule):
        """Remove a rate limiting rule"""
        if rule in self.config.rules:
            self.config.rules.remove(rule)
    
    async def clear_user_limits(self, user_id: str):
        """Clear rate limits for a specific user"""
        # This would require iterating through possible keys
        # Implementation depends on storage backend capabilities
        pass
    
    async def get_usage_stats(
        self,
        identifier: str,
        rule_type: str = "ip"
    ) -> Dict[str, Any]:
        """Get rate limit usage statistics for an identifier"""
        stats = {
            "identifier": identifier,
            "type": rule_type,
            "rules": []
        }
        
        for rule in self.config.rules:
            if rule.per == rule_type:
                key = self._generate_key(rule, identifier, None, None, None)
                count = await self.storage.get_count(key, rule.window)
                reset_time = await self.storage.get_reset_time(key, rule.window)
                
                stats["rules"].append({
                    "window": rule.window,
                    "limit": rule.requests,
                    "current_count": count,
                    "remaining": max(0, rule.requests - count),
                    "reset_time": reset_time
                })
        
        return stats


# Global rate limiter instance
_rate_limiter = None


def get_rate_limiter() -> RateLimiter:
    """Get the global rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware for FastAPI.
    
    This middleware checks rate limits before processing requests
    and adds appropriate headers to responses.
    """
    rate_limiter = get_rate_limiter()
    
    # Extract endpoint for more specific limiting
    endpoint = request.url.path
    
    # Check rate limit
    is_allowed, rate_info = await rate_limiter.check_rate_limit(
        request, endpoint=endpoint
    )
    
    if not is_allowed:
        # Rate limit exceeded
        logger.warning(
            "Rate limit exceeded",
            ip=rate_limiter._get_client_ip(request),
            endpoint=endpoint,
            limit=rate_info.limit,
            retry_after=rate_info.retry_after
        )
        
        headers = {
            "X-RateLimit-Limit": str(rate_info.limit),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(rate_info.reset),
        }
        
        if rate_info.retry_after:
            headers["Retry-After"] = str(rate_info.retry_after)
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Try again in {rate_info.retry_after} seconds.",
                "retry_after": rate_info.retry_after
            },
            headers=headers
        )
    
    # Record the request
    await rate_limiter.record_request(request, endpoint=endpoint)
    
    # Process the request
    response = await call_next(request)
    
    # Add rate limit headers to response
    if rate_info.limit > 0:  # Only add headers if rate limiting is active
        response.headers["X-RateLimit-Limit"] = str(rate_info.limit)
        response.headers["X-RateLimit-Remaining"] = str(rate_info.remaining)
        response.headers["X-RateLimit-Reset"] = str(rate_info.reset)
    
    return response


def rate_limit(
    requests: int,
    window: int,
    per: str = "ip",
    burst: int = 0
):
    """
    Decorator for applying rate limits to specific endpoints.
    
    Args:
        requests: Number of requests allowed
        window: Time window in seconds
        per: Rate limit per what (ip, user, tenant)
        burst: Additional burst allowance
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # This would need to be integrated with FastAPI dependencies
            # For now, it's a placeholder for endpoint-specific rate limiting
            return await func(*args, **kwargs)
        
        # Store rate limit rule on function
        wrapper._rate_limit_rule = RateLimitRule(
            requests=requests,
            window=window,
            per=per,
            burst=burst
        )
        
        return wrapper
    return decorator
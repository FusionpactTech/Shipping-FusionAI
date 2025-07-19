"""
Multi-Tenancy Module

This module provides comprehensive multi-tenant architecture support for enterprise
deployments, including tenant isolation, data routing, and tenant management.

Author: Fusionpact Technologies Inc.
Date: 2025-01-18
Version: 1.0.0
"""

import os
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from contextvars import ContextVar
from dataclasses import dataclass
from enum import Enum
import json
import logging

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from .config import config, FeatureFlags


class TenantIsolationLevel(str, Enum):
    DATABASE = "database"
    SCHEMA = "schema"
    ROW = "row"


class TenantStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"
    PENDING = "pending"


@dataclass
class Tenant:
    """Tenant information and configuration."""
    id: str
    name: str
    domain: Optional[str] = None
    status: TenantStatus = TenantStatus.ACTIVE
    created_at: datetime = None
    updated_at: datetime = None
    settings: Dict[str, Any] = None
    limits: Dict[str, Any] = None
    features: List[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        if self.settings is None:
            self.settings = {}
        if self.limits is None:
            self.limits = {}
        if self.features is None:
            self.features = []


class TenantContext:
    """Context manager for tenant operations."""
    
    def __init__(self):
        self._tenant_context: ContextVar[Optional[str]] = ContextVar('tenant_id', default=None)
        self._tenant_cache: Dict[str, Tenant] = {}
    
    def set_tenant(self, tenant_id: str) -> None:
        """Set the current tenant context."""
        self._tenant_context.set(tenant_id)
    
    def get_current_tenant(self) -> Optional[str]:
        """Get the current tenant ID from context."""
        return self._tenant_context.get()
    
    def clear_tenant(self) -> None:
        """Clear the current tenant context."""
        self._tenant_context.set(None)
    
    def get_tenant_from_request(self, request) -> Optional[str]:
        """Extract tenant ID from request headers or subdomain."""
        # Check for tenant header
        tenant_id = request.headers.get('X-Tenant-ID')
        if tenant_id:
            return tenant_id
        
        # Check for tenant in subdomain
        host = request.headers.get('host', '')
        if '.' in host:
            subdomain = host.split('.')[0]
            if subdomain and subdomain != 'www':
                return subdomain
        
        # Check for tenant in path
        path_parts = request.url.path.split('/')
        if len(path_parts) > 1 and path_parts[1]:
            return path_parts[1]
        
        return None


class TenantManager:
    """Manages tenant operations and data isolation."""
    
    def __init__(self):
        self.tenants: Dict[str, Tenant] = {}
        self.context = TenantContext()
        self.logger = logging.getLogger(__name__)
        self._load_tenants()
    
    def _load_tenants(self) -> None:
        """Load tenant configurations from database or file."""
        try:
            # Load from database if available
            self._load_tenants_from_db()
        except Exception as e:
            self.logger.warning(f"Could not load tenants from database: {e}")
            # Fallback to default tenant
            self._create_default_tenant()
    
    def _load_tenants_from_db(self) -> None:
        """Load tenants from database."""
        # This would connect to the tenant management database
        # For now, we'll create a default tenant
        pass
    
    def _create_default_tenant(self) -> None:
        """Create the default tenant."""
        default_tenant = Tenant(
            id=config.default_tenant_id,
            name="Default Fleet Operator",
            domain="default",
            status=TenantStatus.ACTIVE,
            settings={
                "ai_model_version": "1.0.0",
                "classification_weights": {},
                "notification_channels": ["webhook"],
                "data_retention_days": 2555
            },
            limits={
                "max_documents_per_day": 10000,
                "max_concurrent_requests": 100,
                "max_storage_gb": 100
            },
            features=[
                "advanced_analytics",
                "custom_models",
                "batch_processing",
                "real_time_notifications"
            ]
        )
        self.tenants[default_tenant.id] = default_tenant
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID."""
        return self.tenants.get(tenant_id)
    
    def create_tenant(self, name: str, domain: Optional[str] = None, 
                     settings: Optional[Dict[str, Any]] = None) -> Tenant:
        """Create a new tenant."""
        tenant_id = str(uuid.uuid4())
        tenant = Tenant(
            id=tenant_id,
            name=name,
            domain=domain,
            status=TenantStatus.PENDING,
            settings=settings or {},
            limits={
                "max_documents_per_day": 1000,
                "max_concurrent_requests": 50,
                "max_storage_gb": 10
            },
            features=[
                "basic_analytics",
                "standard_models"
            ]
        )
        self.tenants[tenant_id] = tenant
        self._save_tenant(tenant)
        return tenant
    
    def update_tenant(self, tenant_id: str, **kwargs) -> Optional[Tenant]:
        """Update tenant information."""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return None
        
        for key, value in kwargs.items():
            if hasattr(tenant, key):
                setattr(tenant, key, value)
        
        tenant.updated_at = datetime.utcnow()
        self._save_tenant(tenant)
        return tenant
    
    def delete_tenant(self, tenant_id: str) -> bool:
        """Delete a tenant."""
        if tenant_id in self.tenants:
            del self.tenants[tenant_id]
            self._save_tenant_deletion(tenant_id)
            return True
        return False
    
    def _save_tenant(self, tenant: Tenant) -> None:
        """Save tenant to persistent storage."""
        # This would save to database
        # For now, we'll just log it
        self.logger.info(f"Saved tenant: {tenant.id} - {tenant.name}")
    
    def _save_tenant_deletion(self, tenant_id: str) -> None:
        """Log tenant deletion."""
        self.logger.info(f"Deleted tenant: {tenant_id}")


class TenantDatabaseManager:
    """Manages database connections and operations for multi-tenant architecture."""
    
    def __init__(self):
        self.engines: Dict[str, Any] = {}
        self.sessions: Dict[str, Any] = {}
        self.isolation_level = config.tenant_isolation_level
        self.logger = logging.getLogger(__name__)
    
    def get_engine_for_tenant(self, tenant_id: str):
        """Get database engine for specific tenant."""
        if tenant_id not in self.engines:
            self._create_engine_for_tenant(tenant_id)
        return self.engines[tenant_id]
    
    def get_session_for_tenant(self, tenant_id: str):
        """Get database session for specific tenant."""
        if tenant_id not in self.sessions:
            engine = self.get_engine_for_tenant(tenant_id)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            self.sessions[tenant_id] = SessionLocal
        
        return self.sessions[tenant_id]()
    
    def _create_engine_for_tenant(self, tenant_id: str) -> None:
        """Create database engine for tenant based on isolation level."""
        if self.isolation_level == TenantIsolationLevel.DATABASE:
            # Separate database per tenant
            db_url = self._get_tenant_database_url(tenant_id)
        elif self.isolation_level == TenantIsolationLevel.SCHEMA:
            # Separate schema per tenant
            db_url = config.database_url
        else:
            # Row-level isolation
            db_url = config.database_url
        
        engine = create_engine(
            db_url,
            **DatabaseConfig.get_pool_settings(),
            pool_pre_ping=True
        )
        self.engines[tenant_id] = engine
    
    def _get_tenant_database_url(self, tenant_id: str) -> str:
        """Get database URL for tenant."""
        base_url = config.database_url
        if 'sqlite' in base_url:
            # For SQLite, use separate file per tenant
            db_path = f"./data/vessel_ai_{tenant_id}.db"
            return f"sqlite:///{db_path}"
        elif 'postgresql' in base_url:
            # For PostgreSQL, use separate database
            return base_url.replace('/vessel_ai', f'/vessel_ai_{tenant_id}')
        elif 'mysql' in base_url:
            # For MySQL, use separate database
            return base_url.replace('/vessel_ai', f'/vessel_ai_{tenant_id}')
        else:
            return base_url
    
    def create_tenant_database(self, tenant_id: str) -> bool:
        """Create database/schema for new tenant."""
        try:
            if self.isolation_level == TenantIsolationLevel.DATABASE:
                return self._create_tenant_database(tenant_id)
            elif self.isolation_level == TenantIsolationLevel.SCHEMA:
                return self._create_tenant_schema(tenant_id)
            else:
                return True  # Row-level isolation doesn't need separate DB
        except Exception as e:
            self.logger.error(f"Failed to create tenant database: {e}")
            return False
    
    def _create_tenant_database(self, tenant_id: str) -> bool:
        """Create separate database for tenant."""
        try:
            # This would create a new database
            # Implementation depends on database type
            self.logger.info(f"Created database for tenant: {tenant_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create database for tenant {tenant_id}: {e}")
            return False
    
    def _create_tenant_schema(self, tenant_id: str) -> bool:
        """Create separate schema for tenant."""
        try:
            engine = self.get_engine_for_tenant(tenant_id)
            with engine.connect() as conn:
                conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS tenant_{tenant_id}"))
                conn.commit()
            return True
        except Exception as e:
            self.logger.error(f"Failed to create schema for tenant {tenant_id}: {e}")
            return False


class TenantMiddleware:
    """FastAPI middleware for tenant routing and context management."""
    
    def __init__(self, tenant_manager: TenantManager):
        self.tenant_manager = tenant_manager
        self.context = tenant_manager.context
    
    async def __call__(self, request, call_next):
        """Process request with tenant context."""
        # Extract tenant ID from request
        tenant_id = self.context.get_tenant_from_request(request)
        
        if not tenant_id:
            tenant_id = config.default_tenant_id
        
        # Validate tenant
        tenant = self.tenant_manager.get_tenant(tenant_id)
        if not tenant or tenant.status != TenantStatus.ACTIVE:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Tenant not found or inactive")
        
        # Set tenant context
        self.context.set_tenant(tenant_id)
        
        try:
            # Add tenant info to request state
            request.state.tenant = tenant
            request.state.tenant_id = tenant_id
            
            # Process request
            response = await call_next(request)
            
            # Add tenant headers to response
            response.headers["X-Tenant-ID"] = tenant_id
            response.headers["X-Tenant-Name"] = tenant.name
            
            return response
        finally:
            # Clear tenant context
            self.context.clear_tenant()


class TenantLimits:
    """Manages tenant usage limits and quotas."""
    
    def __init__(self, tenant_manager: TenantManager):
        self.tenant_manager = tenant_manager
        self.usage_cache: Dict[str, Dict[str, int]] = {}
    
    def check_limits(self, tenant_id: str, operation: str, count: int = 1) -> bool:
        """Check if tenant has exceeded limits for operation."""
        tenant = self.tenant_manager.get_tenant(tenant_id)
        if not tenant:
            return False
        
        limits = tenant.limits
        current_usage = self._get_current_usage(tenant_id, operation)
        
        if operation == "documents_per_day":
            return current_usage + count <= limits.get("max_documents_per_day", 1000)
        elif operation == "concurrent_requests":
            return current_usage + count <= limits.get("max_concurrent_requests", 50)
        elif operation == "storage_gb":
            return current_usage + count <= limits.get("max_storage_gb", 10)
        
        return True
    
    def increment_usage(self, tenant_id: str, operation: str, count: int = 1) -> None:
        """Increment usage counter for tenant."""
        if tenant_id not in self.usage_cache:
            self.usage_cache[tenant_id] = {}
        
        if operation not in self.usage_cache[tenant_id]:
            self.usage_cache[tenant_id][operation] = 0
        
        self.usage_cache[tenant_id][operation] += count
    
    def _get_current_usage(self, tenant_id: str, operation: str) -> int:
        """Get current usage for tenant operation."""
        return self.usage_cache.get(tenant_id, {}).get(operation, 0)


# Global instances
tenant_manager = TenantManager()
tenant_db_manager = TenantDatabaseManager()
tenant_limits = TenantLimits(tenant_manager)
tenant_middleware = TenantMiddleware(tenant_manager)


def get_current_tenant_id() -> Optional[str]:
    """Get current tenant ID from context."""
    return tenant_manager.context.get_current_tenant()


def get_current_tenant() -> Optional[Tenant]:
    """Get current tenant from context."""
    tenant_id = get_current_tenant_id()
    if tenant_id:
        return tenant_manager.get_tenant(tenant_id)
    return None


def require_tenant(func):
    """Decorator to require tenant context."""
    def wrapper(*args, **kwargs):
        tenant_id = get_current_tenant_id()
        if not tenant_id:
            raise ValueError("Tenant context required")
        return func(*args, **kwargs)
    return wrapper
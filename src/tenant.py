"""
Multi-Tenant Architecture Module

This module provides comprehensive multi-tenant support for the vessel
maintenance AI system, including tenant isolation, management, and
security features for enterprise deployment.

Author: Fusionpact Technologies Inc.
Date: 2025-01-27
Version: 2.0.0
License: MIT License
"""

import uuid
from typing import Optional, List, Dict, Any, Set
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import structlog
from cryptography.fernet import Fernet
import json

from .config import settings

logger = structlog.get_logger(__name__)
Base = declarative_base()
security = HTTPBearer()


class TenantModel(Base):
    """Database model for tenant information"""
    __tablename__ = "tenants"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    settings = Column(Text)  # JSON string for tenant-specific settings
    subscription_tier = Column(String(50), default="basic")
    max_users = Column(Integer, default=10)
    max_documents_per_month = Column(Integer, default=1000)
    data_retention_days = Column(Integer, default=90)
    
    # Relationships
    users = relationship("TenantUserModel", back_populates="tenant")


class TenantUserModel(Base):
    """Database model for tenant user relationships"""
    __tablename__ = "tenant_users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    user_id = Column(String(255), nullable=False)
    role = Column(String(50), default="user")  # admin, manager, user, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    permissions = Column(Text)  # JSON string for user permissions
    
    # Relationships
    tenant = relationship("TenantModel", back_populates="users")


class Tenant(BaseModel):
    """Pydantic model for tenant data"""
    id: str
    name: str
    domain: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    settings: Dict[str, Any] = {}
    subscription_tier: str = "basic"
    max_users: int = 10
    max_documents_per_month: int = 1000
    data_retention_days: int = 90


class TenantUser(BaseModel):
    """Pydantic model for tenant user data"""
    id: str
    tenant_id: str
    user_id: str
    role: str = "user"
    is_active: bool = True
    created_at: datetime
    permissions: Dict[str, Any] = {}


class TenantCreate(BaseModel):
    """Model for creating new tenants"""
    name: str = Field(..., min_length=1, max_length=255)
    domain: str = Field(..., min_length=1, max_length=255)
    subscription_tier: str = Field(default="basic")
    max_users: int = Field(default=10, ge=1, le=10000)
    max_documents_per_month: int = Field(default=1000, ge=100, le=1000000)
    data_retention_days: int = Field(default=90, ge=30, le=2555)
    settings: Dict[str, Any] = Field(default_factory=dict)


class TenantUpdate(BaseModel):
    """Model for updating tenant information"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None
    subscription_tier: Optional[str] = None
    max_users: Optional[int] = Field(None, ge=1, le=10000)
    max_documents_per_month: Optional[int] = Field(None, ge=100, le=1000000)
    data_retention_days: Optional[int] = Field(None, ge=30, le=2555)
    settings: Optional[Dict[str, Any]] = None


class TenantContext:
    """Thread-local context for current tenant"""
    _current_tenant: Optional[Tenant] = None
    _current_user: Optional[TenantUser] = None
    
    @classmethod
    def set_current_tenant(cls, tenant: Tenant):
        """Set the current tenant for the request context"""
        cls._current_tenant = tenant
    
    @classmethod
    def get_current_tenant(cls) -> Optional[Tenant]:
        """Get the current tenant from the request context"""
        return cls._current_tenant
    
    @classmethod
    def set_current_user(cls, user: TenantUser):
        """Set the current user for the request context"""
        cls._current_user = user
    
    @classmethod
    def get_current_user(cls) -> Optional[TenantUser]:
        """Get the current user from the request context"""
        return cls._current_user
    
    @classmethod
    def clear(cls):
        """Clear the current context"""
        cls._current_tenant = None
        cls._current_user = None


class TenantManager:
    """
    Manager class for tenant operations and multi-tenant support.
    
    This class provides comprehensive tenant management functionality
    including creation, updates, user management, and data isolation.
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.encryption_key = settings.encryption_key or Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
    
    def create_tenant(self, tenant_data: TenantCreate) -> Tenant:
        """
        Create a new tenant with proper validation and setup.
        
        Args:
            tenant_data: Tenant creation data
            
        Returns:
            Created tenant object
            
        Raises:
            HTTPException: If domain already exists or validation fails
        """
        # Check if domain already exists
        existing = self.db.query(TenantModel).filter(
            TenantModel.domain == tenant_data.domain
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Tenant with domain '{tenant_data.domain}' already exists"
            )
        
        # Check tenant limits
        total_tenants = self.db.query(TenantModel).filter(
            TenantModel.is_active == True
        ).count()
        
        if total_tenants >= settings.max_tenants:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum number of tenants ({settings.max_tenants}) reached"
            )
        
        # Create tenant
        tenant_model = TenantModel(
            name=tenant_data.name,
            domain=tenant_data.domain,
            subscription_tier=tenant_data.subscription_tier,
            max_users=tenant_data.max_users,
            max_documents_per_month=tenant_data.max_documents_per_month,
            data_retention_days=tenant_data.data_retention_days,
            settings=self._encrypt_settings(tenant_data.settings)
        )
        
        self.db.add(tenant_model)
        self.db.commit()
        self.db.refresh(tenant_model)
        
        logger.info("Tenant created", tenant_id=tenant_model.id, domain=tenant_data.domain)
        
        return self._model_to_tenant(tenant_model)
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID"""
        tenant_model = self.db.query(TenantModel).filter(
            TenantModel.id == tenant_id
        ).first()
        
        if tenant_model:
            return self._model_to_tenant(tenant_model)
        return None
    
    def get_tenant_by_domain(self, domain: str) -> Optional[Tenant]:
        """Get tenant by domain"""
        tenant_model = self.db.query(TenantModel).filter(
            TenantModel.domain == domain
        ).first()
        
        if tenant_model:
            return self._model_to_tenant(tenant_model)
        return None
    
    def update_tenant(self, tenant_id: str, update_data: TenantUpdate) -> Optional[Tenant]:
        """
        Update tenant information.
        
        Args:
            tenant_id: ID of tenant to update
            update_data: Update data
            
        Returns:
            Updated tenant object or None if not found
        """
        tenant_model = self.db.query(TenantModel).filter(
            TenantModel.id == tenant_id
        ).first()
        
        if not tenant_model:
            return None
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        
        for field, value in update_dict.items():
            if field == "settings":
                setattr(tenant_model, field, self._encrypt_settings(value))
            else:
                setattr(tenant_model, field, value)
        
        tenant_model.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(tenant_model)
        
        logger.info("Tenant updated", tenant_id=tenant_id)
        
        return self._model_to_tenant(tenant_model)
    
    def delete_tenant(self, tenant_id: str) -> bool:
        """
        Soft delete a tenant (mark as inactive).
        
        Args:
            tenant_id: ID of tenant to delete
            
        Returns:
            True if deleted, False if not found
        """
        tenant_model = self.db.query(TenantModel).filter(
            TenantModel.id == tenant_id
        ).first()
        
        if not tenant_model:
            return False
        
        tenant_model.is_active = False
        tenant_model.updated_at = datetime.utcnow()
        self.db.commit()
        
        logger.info("Tenant deactivated", tenant_id=tenant_id)
        
        return True
    
    def list_tenants(self, active_only: bool = True) -> List[Tenant]:
        """List all tenants"""
        query = self.db.query(TenantModel)
        
        if active_only:
            query = query.filter(TenantModel.is_active == True)
        
        tenant_models = query.all()
        return [self._model_to_tenant(tm) for tm in tenant_models]
    
    def add_user_to_tenant(
        self,
        tenant_id: str,
        user_id: str,
        role: str = "user",
        permissions: Dict[str, Any] = None
    ) -> TenantUser:
        """
        Add a user to a tenant with specified role and permissions.
        
        Args:
            tenant_id: ID of the tenant
            user_id: ID of the user to add
            role: User role (admin, manager, user, viewer)
            permissions: User-specific permissions
            
        Returns:
            Created tenant user object
            
        Raises:
            HTTPException: If tenant not found or user limit exceeded
        """
        # Check if tenant exists
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        # Check user limit
        user_count = self.db.query(TenantUserModel).filter(
            TenantUserModel.tenant_id == tenant_id,
            TenantUserModel.is_active == True
        ).count()
        
        if user_count >= tenant.max_users:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum number of users ({tenant.max_users}) reached for this tenant"
            )
        
        # Check if user already exists in tenant
        existing = self.db.query(TenantUserModel).filter(
            TenantUserModel.tenant_id == tenant_id,
            TenantUserModel.user_id == user_id
        ).first()
        
        if existing:
            # Reactivate if inactive
            if not existing.is_active:
                existing.is_active = True
                existing.role = role
                existing.permissions = self._encrypt_settings(permissions or {})
                self.db.commit()
                self.db.refresh(existing)
                return self._model_to_tenant_user(existing)
            else:
                raise HTTPException(
                    status_code=400,
                    detail="User already exists in this tenant"
                )
        
        # Create new tenant user
        tenant_user_model = TenantUserModel(
            tenant_id=tenant_id,
            user_id=user_id,
            role=role,
            permissions=self._encrypt_settings(permissions or {})
        )
        
        self.db.add(tenant_user_model)
        self.db.commit()
        self.db.refresh(tenant_user_model)
        
        logger.info("User added to tenant", tenant_id=tenant_id, user_id=user_id, role=role)
        
        return self._model_to_tenant_user(tenant_user_model)
    
    def remove_user_from_tenant(self, tenant_id: str, user_id: str) -> bool:
        """Remove user from tenant (soft delete)"""
        tenant_user = self.db.query(TenantUserModel).filter(
            TenantUserModel.tenant_id == tenant_id,
            TenantUserModel.user_id == user_id
        ).first()
        
        if not tenant_user:
            return False
        
        tenant_user.is_active = False
        self.db.commit()
        
        logger.info("User removed from tenant", tenant_id=tenant_id, user_id=user_id)
        
        return True
    
    def get_user_tenants(self, user_id: str) -> List[Tenant]:
        """Get all tenants for a user"""
        tenant_users = self.db.query(TenantUserModel).filter(
            TenantUserModel.user_id == user_id,
            TenantUserModel.is_active == True
        ).all()
        
        tenants = []
        for tu in tenant_users:
            tenant = self.get_tenant(tu.tenant_id)
            if tenant and tenant.is_active:
                tenants.append(tenant)
        
        return tenants
    
    def get_tenant_users(self, tenant_id: str) -> List[TenantUser]:
        """Get all users for a tenant"""
        tenant_users = self.db.query(TenantUserModel).filter(
            TenantUserModel.tenant_id == tenant_id,
            TenantUserModel.is_active == True
        ).all()
        
        return [self._model_to_tenant_user(tu) for tu in tenant_users]
    
    def validate_tenant_access(self, tenant_id: str, user_id: str) -> bool:
        """Validate if user has access to tenant"""
        tenant_user = self.db.query(TenantUserModel).filter(
            TenantUserModel.tenant_id == tenant_id,
            TenantUserModel.user_id == user_id,
            TenantUserModel.is_active == True
        ).first()
        
        return tenant_user is not None
    
    def get_tenant_usage_stats(self, tenant_id: str) -> Dict[str, Any]:
        """Get usage statistics for a tenant"""
        # This would integrate with your analytics system
        # For now, returning basic structure
        return {
            "documents_processed_this_month": 0,
            "active_users": len(self.get_tenant_users(tenant_id)),
            "storage_used_mb": 0,
            "api_calls_this_month": 0
        }
    
    def _encrypt_settings(self, settings: Dict[str, Any]) -> str:
        """Encrypt tenant settings for storage"""
        if not settings:
            return ""
        
        settings_json = json.dumps(settings)
        if settings.encryption_enabled:
            encrypted = self.cipher.encrypt(settings_json.encode())
            return encrypted.decode()
        return settings_json
    
    def _decrypt_settings(self, encrypted_settings: str) -> Dict[str, Any]:
        """Decrypt tenant settings from storage"""
        if not encrypted_settings:
            return {}
        
        try:
            if settings.encryption_enabled:
                decrypted = self.cipher.decrypt(encrypted_settings.encode())
                return json.loads(decrypted.decode())
            else:
                return json.loads(encrypted_settings)
        except Exception as e:
            logger.error("Failed to decrypt tenant settings", error=str(e))
            return {}
    
    def _model_to_tenant(self, tenant_model: TenantModel) -> Tenant:
        """Convert database model to Pydantic model"""
        return Tenant(
            id=tenant_model.id,
            name=tenant_model.name,
            domain=tenant_model.domain,
            is_active=tenant_model.is_active,
            created_at=tenant_model.created_at,
            updated_at=tenant_model.updated_at,
            settings=self._decrypt_settings(tenant_model.settings or ""),
            subscription_tier=tenant_model.subscription_tier,
            max_users=tenant_model.max_users,
            max_documents_per_month=tenant_model.max_documents_per_month,
            data_retention_days=tenant_model.data_retention_days
        )
    
    def _model_to_tenant_user(self, tenant_user_model: TenantUserModel) -> TenantUser:
        """Convert database model to Pydantic model"""
        return TenantUser(
            id=tenant_user_model.id,
            tenant_id=tenant_user_model.tenant_id,
            user_id=tenant_user_model.user_id,
            role=tenant_user_model.role,
            is_active=tenant_user_model.is_active,
            created_at=tenant_user_model.created_at,
            permissions=self._decrypt_settings(tenant_user_model.permissions or "")
        )


def extract_tenant_from_request(request: Request) -> Optional[str]:
    """
    Extract tenant ID from request headers or subdomain.
    
    This function checks multiple sources for tenant identification:
    1. X-Tenant-ID header
    2. Subdomain extraction
    3. Query parameter
    """
    # Check X-Tenant-ID header
    tenant_id = request.headers.get("X-Tenant-ID")
    if tenant_id:
        return tenant_id
    
    # Check subdomain
    host = request.headers.get("host", "")
    if "." in host:
        subdomain = host.split(".")[0]
        if subdomain != "www" and subdomain != "api":
            # Look up tenant by domain
            # This would need database access
            return subdomain
    
    # Check query parameter
    tenant_id = request.query_params.get("tenant_id")
    if tenant_id:
        return tenant_id
    
    return None


async def get_current_tenant(
    request: Request,
    db: Session = Depends(lambda: None)  # Replace with your DB dependency
) -> Tenant:
    """
    Dependency to get current tenant from request context.
    
    This function extracts tenant information from the request
    and validates access permissions.
    """
    if not settings.multi_tenant_enabled:
        # Return default tenant if multi-tenancy is disabled
        return Tenant(
            id=settings.default_tenant_id,
            name="Default Tenant",
            domain="default",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    tenant_id = extract_tenant_from_request(request)
    
    if not tenant_id:
        raise HTTPException(
            status_code=400,
            detail="Tenant ID required. Provide via X-Tenant-ID header, subdomain, or tenant_id parameter"
        )
    
    tenant_manager = TenantManager(db)
    tenant = tenant_manager.get_tenant(tenant_id)
    
    if not tenant:
        tenant = tenant_manager.get_tenant_by_domain(tenant_id)
    
    if not tenant or not tenant.is_active:
        raise HTTPException(
            status_code=404,
            detail="Tenant not found or inactive"
        )
    
    # Set tenant in context
    TenantContext.set_current_tenant(tenant)
    
    return tenant


def require_tenant_permission(permission: str):
    """
    Decorator to require specific tenant permission.
    
    Args:
        permission: Required permission string
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_user = TenantContext.get_current_user()
            if not current_user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            if permission not in current_user.permissions:
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission '{permission}' required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_tenant_role(min_role: str):
    """
    Decorator to require minimum tenant role.
    
    Role hierarchy: viewer < user < manager < admin
    """
    role_hierarchy = {"viewer": 0, "user": 1, "manager": 2, "admin": 3}
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_user = TenantContext.get_current_user()
            if not current_user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            user_level = role_hierarchy.get(current_user.role, 0)
            required_level = role_hierarchy.get(min_role, 3)
            
            if user_level < required_level:
                raise HTTPException(
                    status_code=403,
                    detail=f"Role '{min_role}' or higher required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
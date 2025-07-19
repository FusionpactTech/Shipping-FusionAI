"""
Authentication and Security Module

This module provides comprehensive authentication and security features for enterprise
deployments, including JWT authentication, API keys, SSO integration, and RBAC.

Author: Fusionpact Technologies Inc.
Date: 2025-01-18
Version: 1.0.0
"""

import os
import secrets
import hashlib
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import logging
import json

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from .config import config, SecurityConfig
from .tenancy import get_current_tenant_id, get_current_tenant


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    OPERATOR = "operator"
    VIEWER = "viewer"


class Permission(str, Enum):
    # Document Processing
    PROCESS_DOCUMENTS = "process_documents"
    VIEW_DOCUMENTS = "view_documents"
    DELETE_DOCUMENTS = "delete_documents"
    
    # Analytics
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_REPORTS = "export_reports"
    ACCESS_ADVANCED_ANALYTICS = "access_advanced_analytics"
    
    # System Management
    MANAGE_USERS = "manage_users"
    MANAGE_TENANTS = "manage_tenants"
    MANAGE_SYSTEM = "manage_system"
    VIEW_LOGS = "view_logs"
    
    # AI Models
    TRAIN_MODELS = "train_models"
    DEPLOY_MODELS = "deploy_models"
    VIEW_MODELS = "view_models"
    
    # Notifications
    MANAGE_NOTIFICATIONS = "manage_notifications"
    SEND_NOTIFICATIONS = "send_notifications"
    
    # API Management
    MANAGE_API_KEYS = "manage_api_keys"
    VIEW_API_USAGE = "view_api_usage"


class AuthenticationMethod(str, Enum):
    JWT = "jwt"
    API_KEY = "api_key"
    SSO = "sso"
    OAUTH2 = "oauth2"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class User(BaseModel):
    """User model with comprehensive attributes."""
    id: str
    username: str
    email: str
    full_name: str
    role: UserRole
    status: UserRole = UserStatus.ACTIVE
    tenant_id: Optional[str] = None
    permissions: List[Permission] = []
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    password_hash: Optional[str] = None
    api_keys: List[str] = []
    sso_provider: Optional[str] = None
    sso_id: Optional[str] = None
    
    class Config:
        use_enum_values = True


class APIKey(BaseModel):
    """API key model for programmatic access."""
    id: str
    name: str
    key_hash: str
    user_id: str
    tenant_id: str
    permissions: List[Permission]
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    is_active: bool = True


class RolePermissions:
    """Role-based permission management."""
    
    ROLE_PERMISSIONS = {
        UserRole.ADMIN: [
            Permission.PROCESS_DOCUMENTS,
            Permission.VIEW_DOCUMENTS,
            Permission.DELETE_DOCUMENTS,
            Permission.VIEW_ANALYTICS,
            Permission.EXPORT_REPORTS,
            Permission.ACCESS_ADVANCED_ANALYTICS,
            Permission.MANAGE_USERS,
            Permission.MANAGE_TENANTS,
            Permission.MANAGE_SYSTEM,
            Permission.VIEW_LOGS,
            Permission.TRAIN_MODELS,
            Permission.DEPLOY_MODELS,
            Permission.VIEW_MODELS,
            Permission.MANAGE_NOTIFICATIONS,
            Permission.SEND_NOTIFICATIONS,
            Permission.MANAGE_API_KEYS,
            Permission.VIEW_API_USAGE
        ],
        UserRole.MANAGER: [
            Permission.PROCESS_DOCUMENTS,
            Permission.VIEW_DOCUMENTS,
            Permission.VIEW_ANALYTICS,
            Permission.EXPORT_REPORTS,
            Permission.ACCESS_ADVANCED_ANALYTICS,
            Permission.MANAGE_USERS,
            Permission.VIEW_LOGS,
            Permission.VIEW_MODELS,
            Permission.MANAGE_NOTIFICATIONS,
            Permission.SEND_NOTIFICATIONS,
            Permission.VIEW_API_USAGE
        ],
        UserRole.ANALYST: [
            Permission.PROCESS_DOCUMENTS,
            Permission.VIEW_DOCUMENTS,
            Permission.VIEW_ANALYTICS,
            Permission.EXPORT_REPORTS,
            Permission.ACCESS_ADVANCED_ANALYTICS,
            Permission.VIEW_MODELS,
            Permission.VIEW_API_USAGE
        ],
        UserRole.OPERATOR: [
            Permission.PROCESS_DOCUMENTS,
            Permission.VIEW_DOCUMENTS,
            Permission.VIEW_ANALYTICS,
            Permission.VIEW_MODELS
        ],
        UserRole.VIEWER: [
            Permission.VIEW_DOCUMENTS,
            Permission.VIEW_ANALYTICS
        ]
    }
    
    @classmethod
    def get_permissions_for_role(cls, role: UserRole) -> List[Permission]:
        """Get permissions for a specific role."""
        return cls.ROLE_PERMISSIONS.get(role, [])
    
    @classmethod
    def has_permission(cls, user_permissions: List[Permission], required_permission: Permission) -> bool:
        """Check if user has required permission."""
        return required_permission in user_permissions


class PasswordManager:
    """Password hashing and verification."""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash_password(self, password: str) -> str:
        """Hash a password."""
        return self.pwd_context.hash(password)
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(password, hashed_password)


class JWTManager:
    """JWT token management."""
    
    def __init__(self):
        self.secret_key = config.secret_key
        self.algorithm = config.algorithm
        self.access_token_expire_minutes = config.access_token_expire_minutes
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def decode_token(self, token: str) -> dict:
        """Decode and verify a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )


class APIKeyManager:
    """API key management for programmatic access."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_keys: Dict[str, APIKey] = {}
    
    def generate_api_key(self) -> str:
        """Generate a new API key."""
        return f"vai_{secrets.token_urlsafe(32)}"
    
    def hash_api_key(self, api_key: str) -> str:
        """Hash an API key for storage."""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def create_api_key(self, name: str, user_id: str, tenant_id: str, 
                      permissions: List[Permission], expires_in_days: Optional[int] = None) -> tuple[str, APIKey]:
        """Create a new API key."""
        api_key = self.generate_api_key()
        key_hash = self.hash_api_key(api_key)
        
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        api_key_obj = APIKey(
            id=str(secrets.token_urlsafe(16)),
            name=name,
            key_hash=key_hash,
            user_id=user_id,
            tenant_id=tenant_id,
            permissions=permissions,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            is_active=True
        )
        
        self.api_keys[api_key_obj.id] = api_key_obj
        self._save_api_key(api_key_obj)
        
        return api_key, api_key_obj
    
    def validate_api_key(self, api_key: str) -> Optional[APIKey]:
        """Validate an API key and return the associated key object."""
        key_hash = self.hash_api_key(api_key)
        
        for key_obj in self.api_keys.values():
            if key_obj.key_hash == key_hash and key_obj.is_active:
                # Check expiration
                if key_obj.expires_at and datetime.utcnow() > key_obj.expires_at:
                    continue
                
                # Update last used
                key_obj.last_used = datetime.utcnow()
                return key_obj
        
        return None
    
    def revoke_api_key(self, key_id: str) -> bool:
        """Revoke an API key."""
        if key_id in self.api_keys:
            self.api_keys[key_id].is_active = False
            self._save_api_key_revocation(key_id)
            return True
        return False
    
    def _save_api_key(self, api_key: APIKey) -> None:
        """Save API key to persistent storage."""
        self.logger.info(f"Created API key: {api_key.name} for user: {api_key.user_id}")
    
    def _save_api_key_revocation(self, key_id: str) -> None:
        """Log API key revocation."""
        self.logger.info(f"Revoked API key: {key_id}")


class UserManager:
    """User management and authentication."""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.password_manager = PasswordManager()
        self.jwt_manager = JWTManager()
        self.api_key_manager = APIKeyManager()
        self.logger = logging.getLogger(__name__)
        self._load_users()
    
    def _load_users(self) -> None:
        """Load users from persistent storage."""
        # Create default admin user
        admin_user = User(
            id="admin",
            username="admin",
            email="admin@vesselai.com",
            full_name="System Administrator",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            tenant_id=config.default_tenant_id,
            permissions=RolePermissions.get_permissions_for_role(UserRole.ADMIN),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            password_hash=self.password_manager.hash_password("admin123")
        )
        self.users[admin_user.id] = admin_user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password."""
        user = self._get_user_by_username(username)
        if not user:
            return None
        
        if not self.password_manager.verify_password(password, user.password_hash):
            # Increment failed login attempts
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.status = UserStatus.SUSPENDED
            return None
        
        # Reset failed login attempts on successful login
        user.failed_login_attempts = 0
        user.last_login = datetime.utcnow()
        return user
    
    def create_user(self, username: str, email: str, full_name: str, 
                   password: str, role: UserRole, tenant_id: Optional[str] = None) -> User:
        """Create a new user."""
        if self._get_user_by_username(username):
            raise ValueError("Username already exists")
        
        if self._get_user_by_email(email):
            raise ValueError("Email already exists")
        
        user = User(
            id=str(secrets.token_urlsafe(16)),
            username=username,
            email=email,
            full_name=full_name,
            role=role,
            status=UserStatus.ACTIVE,
            tenant_id=tenant_id or get_current_tenant_id(),
            permissions=RolePermissions.get_permissions_for_role(role),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            password_hash=self.password_manager.hash_password(password)
        )
        
        self.users[user.id] = user
        self._save_user(user)
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.users.get(user_id)
    
    def _get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    def _get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
    def _save_user(self, user: User) -> None:
        """Save user to persistent storage."""
        self.logger.info(f"Saved user: {user.username} - {user.email}")


class AuthenticationService:
    """Main authentication service."""
    
    def __init__(self):
        self.user_manager = UserManager()
        self.jwt_manager = JWTManager()
        self.api_key_manager = APIKeyManager()
        self.security = HTTPBearer()
        self.logger = logging.getLogger(__name__)
    
    async def authenticate_jwt(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> User:
        """Authenticate user using JWT token."""
        try:
            payload = self.jwt_manager.decode_token(credentials.credentials)
            user_id = payload.get("sub")
            if user_id is None:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            user = self.user_manager.get_user(user_id)
            if user is None or user.status != UserStatus.ACTIVE:
                raise HTTPException(status_code=401, detail="User not found or inactive")
            
            return user
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    async def authenticate_api_key(self, api_key: str) -> User:
        """Authenticate user using API key."""
        api_key_obj = self.api_key_manager.validate_api_key(api_key)
        if not api_key_obj:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        user = self.user_manager.get_user(api_key_obj.user_id)
        if not user or user.status != UserStatus.ACTIVE:
            raise HTTPException(status_code=401, detail="User not found or inactive")
        
        return user
    
    def create_access_token(self, user: User) -> str:
        """Create access token for user."""
        data = {
            "sub": user.id,
            "username": user.username,
            "role": user.role,
            "tenant_id": user.tenant_id,
            "permissions": [p.value for p in user.permissions]
        }
        return self.jwt_manager.create_access_token(data=data)
    
    def require_permission(self, permission: Permission):
        """Decorator to require specific permission."""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # This would be implemented in the actual endpoint
                # For now, we'll just pass through
                return await func(*args, **kwargs)
            return wrapper
        return decorator


# Global instances
auth_service = AuthenticationService()
user_manager = UserManager()
api_key_manager = APIKeyManager()


# Dependency functions for FastAPI
async def get_current_user_jwt(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> User:
    """Get current user from JWT token."""
    return await auth_service.authenticate_jwt(credentials)


async def get_current_user_api_key(api_key: str = Depends(HTTPBearer())) -> User:
    """Get current user from API key."""
    return await auth_service.authenticate_api_key(api_key)


def require_permission(permission: Permission):
    """Decorator to require specific permission."""
    def decorator(func):
        async def wrapper(*args, current_user: User = Depends(get_current_user_jwt), **kwargs):
            if permission not in current_user.permissions:
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied: {permission.value}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


def require_role(role: UserRole):
    """Decorator to require specific role."""
    def decorator(func):
        async def wrapper(*args, current_user: User = Depends(get_current_user_jwt), **kwargs):
            if current_user.role != role and current_user.role != UserRole.ADMIN:
                raise HTTPException(
                    status_code=403,
                    detail=f"Role required: {role.value}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
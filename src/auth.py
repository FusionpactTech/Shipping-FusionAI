"""
Enterprise Authentication and Security Module

This module provides comprehensive authentication and security features
for the vessel maintenance AI system, including multiple auth providers,
role-based access control, encryption, and audit logging.

Author: Fusionpact Technologies Inc.
Date: 2025-01-27
Version: 2.0.0
License: MIT License
"""

import uuid
import hashlib
import secrets
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
import structlog
from cryptography.fernet import Fernet
import ldap
from authlib.integrations.requests_client import OAuth2Session
import json

from .config import settings, AuthProvider
from .tenant import TenantContext, Tenant

logger = structlog.get_logger(__name__)
Base = declarative_base()

# Security configurations
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)
security = HTTPBearer(auto_error=False)


class UserModel(Base):
    """Database model for user information"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255))
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    password_changed_at = Column(DateTime)
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255))
    profile_data = Column(Text)  # JSON string for additional profile data


class SessionModel(Base):
    """Database model for user sessions"""
    __tablename__ = "user_sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    refresh_token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    refresh_expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    is_active = Column(Boolean, default=True)


class AuditLogModel(Base):
    """Database model for audit logs"""
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36))
    user_id = Column(String(36))
    action = Column(String(255), nullable=False)
    resource_type = Column(String(100))
    resource_id = Column(String(255))
    details = Column(Text)  # JSON string for action details
    ip_address = Column(String(45))
    user_agent = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50))  # success, failure, error


class User(BaseModel):
    """Pydantic model for user data"""
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    two_factor_enabled: bool = False
    profile_data: Dict[str, Any] = {}


class UserCreate(BaseModel):
    """Model for creating new users"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    is_superuser: bool = False
    profile_data: Dict[str, Any] = Field(default_factory=dict)


class UserUpdate(BaseModel):
    """Model for updating user information"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None
    profile_data: Optional[Dict[str, Any]] = None


class UserLogin(BaseModel):
    """Model for user login"""
    username: str
    password: str
    tenant_id: Optional[str] = None


class Token(BaseModel):
    """Model for JWT tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Model for token payload data"""
    user_id: Optional[str] = None
    username: Optional[str] = None
    tenant_id: Optional[str] = None
    scopes: List[str] = []


class AuditLog(BaseModel):
    """Model for audit log entries"""
    id: str
    tenant_id: Optional[str]
    user_id: Optional[str]
    action: str
    resource_type: Optional[str]
    resource_id: Optional[str]
    details: Dict[str, Any] = {}
    ip_address: Optional[str]
    user_agent: Optional[str]
    timestamp: datetime
    status: str


class AuthManager:
    """
    Comprehensive authentication manager supporting multiple auth providers.
    
    This class provides authentication, authorization, session management,
    and security features for the vessel maintenance AI system.
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.encryption_key = settings.encryption_key or Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
    
    def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user with proper validation and security.
        
        Args:
            user_data: User creation data
            
        Returns:
            Created user object
            
        Raises:
            HTTPException: If username/email already exists or validation fails
        """
        # Check if username already exists
        existing_username = self.db.query(UserModel).filter(
            UserModel.username == user_data.username
        ).first()
        
        if existing_username:
            raise HTTPException(
                status_code=400,
                detail="Username already registered"
            )
        
        # Check if email already exists
        existing_email = self.db.query(UserModel).filter(
            UserModel.email == user_data.email
        ).first()
        
        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        
        # Validate password strength
        self._validate_password_strength(user_data.password)
        
        # Create user
        hashed_password = self._hash_password(user_data.password)
        
        user_model = UserModel(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_superuser=user_data.is_superuser,
            password_changed_at=datetime.utcnow(),
            profile_data=self._encrypt_data(user_data.profile_data)
        )
        
        self.db.add(user_model)
        self.db.commit()
        self.db.refresh(user_model)
        
        logger.info("User created", user_id=user_model.id, username=user_data.username)
        
        return self._model_to_user(user_model)
    
    def authenticate_user(
        self,
        username: str,
        password: str,
        tenant_id: Optional[str] = None,
        request: Optional[Request] = None
    ) -> Optional[User]:
        """
        Authenticate user with multiple auth provider support.
        
        Args:
            username: Username or email
            password: User password
            tenant_id: Optional tenant ID for multi-tenant auth
            request: FastAPI request object for audit logging
            
        Returns:
            Authenticated user object or None
        """
        # Get user from database
        user_model = self._get_user_by_username_or_email(username)
        
        if not user_model:
            self._log_audit(
                action="login_failed",
                details={"reason": "user_not_found", "username": username},
                request=request
            )
            return None
        
        # Check if account is locked
        if self._is_account_locked(user_model):
            self._log_audit(
                action="login_failed",
                user_id=user_model.id,
                details={"reason": "account_locked"},
                request=request
            )
            return None
        
        # Authenticate based on provider
        if settings.auth_provider == AuthProvider.LOCAL:
            authenticated = self._verify_password(password, user_model.hashed_password)
        elif settings.auth_provider == AuthProvider.LDAP:
            authenticated = self._authenticate_ldap(username, password)
        elif settings.auth_provider == AuthProvider.OAUTH2:
            authenticated = self._authenticate_oauth2(username, password)
        else:
            authenticated = False
        
        if authenticated:
            # Reset failed login attempts
            user_model.failed_login_attempts = 0
            user_model.locked_until = None
            user_model.last_login = datetime.utcnow()
            self.db.commit()
            
            self._log_audit(
                action="login_success",
                user_id=user_model.id,
                tenant_id=tenant_id,
                request=request
            )
            
            return self._model_to_user(user_model)
        else:
            # Increment failed login attempts
            user_model.failed_login_attempts += 1
            
            # Lock account after 5 failed attempts
            if user_model.failed_login_attempts >= 5:
                user_model.locked_until = datetime.utcnow() + timedelta(minutes=30)
            
            self.db.commit()
            
            self._log_audit(
                action="login_failed",
                user_id=user_model.id,
                details={"reason": "invalid_credentials"},
                request=request
            )
            
            return None
    
    def create_tokens(
        self,
        user: User,
        tenant_id: Optional[str] = None,
        request: Optional[Request] = None
    ) -> Token:
        """
        Create JWT access and refresh tokens for authenticated user.
        
        Args:
            user: Authenticated user
            tenant_id: Optional tenant ID
            request: FastAPI request object
            
        Returns:
            Token object with access and refresh tokens
        """
        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token_data = {
            "sub": user.id,
            "username": user.username,
            "tenant_id": tenant_id,
            "exp": datetime.utcnow() + access_token_expires,
            "type": "access"
        }
        access_token = jwt.encode(
            access_token_data,
            settings.secret_key,
            algorithm="HS256"
        )
        
        # Create refresh token
        refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)
        refresh_token_data = {
            "sub": user.id,
            "exp": datetime.utcnow() + refresh_token_expires,
            "type": "refresh"
        }
        refresh_token = jwt.encode(
            refresh_token_data,
            settings.secret_key,
            algorithm="HS256"
        )
        
        # Store session in database
        session_model = SessionModel(
            user_id=user.id,
            session_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() + access_token_expires,
            refresh_expires_at=datetime.utcnow() + refresh_token_expires,
            ip_address=self._get_client_ip(request),
            user_agent=request.headers.get("user-agent") if request else None
        )
        
        self.db.add(session_model)
        self.db.commit()
        
        self._log_audit(
            action="token_created",
            user_id=user.id,
            tenant_id=tenant_id,
            request=request
        )
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(access_token_expires.total_seconds())
        )
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token to verify
            
        Returns:
            Token data if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=["HS256"]
            )
            
            user_id = payload.get("sub")
            if user_id is None:
                return None
            
            # Check if session is still active
            session = self.db.query(SessionModel).filter(
                SessionModel.session_token == token,
                SessionModel.is_active == True
            ).first()
            
            if not session or session.expires_at < datetime.utcnow():
                return None
            
            # Update last accessed time
            session.last_accessed = datetime.utcnow()
            self.db.commit()
            
            return TokenData(
                user_id=user_id,
                username=payload.get("username"),
                tenant_id=payload.get("tenant_id"),
                scopes=payload.get("scopes", [])
            )
            
        except JWTError:
            return None
    
    def refresh_token(self, refresh_token: str) -> Optional[Token]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New token pair if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                refresh_token,
                settings.secret_key,
                algorithms=["HS256"]
            )
            
            user_id = payload.get("sub")
            if user_id is None or payload.get("type") != "refresh":
                return None
            
            # Check if refresh token is still valid
            session = self.db.query(SessionModel).filter(
                SessionModel.refresh_token == refresh_token,
                SessionModel.is_active == True
            ).first()
            
            if not session or session.refresh_expires_at < datetime.utcnow():
                return None
            
            # Get user
            user = self.get_user(user_id)
            if not user or not user.is_active:
                return None
            
            # Create new tokens
            new_tokens = self.create_tokens(user)
            
            # Deactivate old session
            session.is_active = False
            self.db.commit()
            
            return new_tokens
            
        except JWTError:
            return None
    
    def logout(self, token: str) -> bool:
        """
        Logout user by invalidating session.
        
        Args:
            token: Access token to invalidate
            
        Returns:
            True if successfully logged out
        """
        session = self.db.query(SessionModel).filter(
            SessionModel.session_token == token
        ).first()
        
        if session:
            session.is_active = False
            self.db.commit()
            
            self._log_audit(
                action="logout",
                user_id=session.user_id
            )
            
            return True
        
        return False
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        user_model = self.db.query(UserModel).filter(
            UserModel.id == user_id
        ).first()
        
        if user_model:
            return self._model_to_user(user_model)
        return None
    
    def update_user(self, user_id: str, update_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        user_model = self.db.query(UserModel).filter(
            UserModel.id == user_id
        ).first()
        
        if not user_model:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        
        for field, value in update_dict.items():
            if field == "profile_data":
                setattr(user_model, field, self._encrypt_data(value))
            else:
                setattr(user_model, field, value)
        
        user_model.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user_model)
        
        return self._model_to_user(user_model)
    
    def change_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str
    ) -> bool:
        """Change user password"""
        user_model = self.db.query(UserModel).filter(
            UserModel.id == user_id
        ).first()
        
        if not user_model:
            return False
        
        # Verify current password
        if not self._verify_password(current_password, user_model.hashed_password):
            return False
        
        # Validate new password
        self._validate_password_strength(new_password)
        
        # Update password
        user_model.hashed_password = self._hash_password(new_password)
        user_model.password_changed_at = datetime.utcnow()
        self.db.commit()
        
        self._log_audit(
            action="password_changed",
            user_id=user_id
        )
        
        return True
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def _validate_password_strength(self, password: str):
        """Validate password meets security requirements"""
        if len(password) < 8:
            raise HTTPException(
                status_code=400,
                detail="Password must be at least 8 characters long"
            )
        
        if not any(c.isupper() for c in password):
            raise HTTPException(
                status_code=400,
                detail="Password must contain at least one uppercase letter"
            )
        
        if not any(c.islower() for c in password):
            raise HTTPException(
                status_code=400,
                detail="Password must contain at least one lowercase letter"
            )
        
        if not any(c.isdigit() for c in password):
            raise HTTPException(
                status_code=400,
                detail="Password must contain at least one digit"
            )
    
    def _get_user_by_username_or_email(self, identifier: str) -> Optional[UserModel]:
        """Get user by username or email"""
        return self.db.query(UserModel).filter(
            (UserModel.username == identifier) | (UserModel.email == identifier)
        ).first()
    
    def _is_account_locked(self, user_model: UserModel) -> bool:
        """Check if user account is locked"""
        if user_model.locked_until:
            return datetime.utcnow() < user_model.locked_until
        return False
    
    def _authenticate_ldap(self, username: str, password: str) -> bool:
        """Authenticate user against LDAP server"""
        if not settings.ldap_server:
            return False
        
        try:
            conn = ldap.initialize(f"ldap://{settings.ldap_server}:{settings.ldap_port}")
            user_dn = f"uid={username},{settings.ldap_base_dn}"
            conn.simple_bind_s(user_dn, password)
            conn.unbind()
            return True
        except ldap.INVALID_CREDENTIALS:
            return False
        except Exception as e:
            logger.error("LDAP authentication error", error=str(e))
            return False
    
    def _authenticate_oauth2(self, username: str, password: str) -> bool:
        """Authenticate user against OAuth2 provider"""
        # Implementation would depend on specific OAuth2 provider
        # This is a placeholder for OAuth2 authentication
        return False
    
    def _encrypt_data(self, data: Any) -> str:
        """Encrypt sensitive data for storage"""
        if not data:
            return ""
        
        data_json = json.dumps(data)
        if settings.encryption_enabled:
            encrypted = self.cipher.encrypt(data_json.encode())
            return encrypted.decode()
        return data_json
    
    def _decrypt_data(self, encrypted_data: str) -> Any:
        """Decrypt sensitive data from storage"""
        if not encrypted_data:
            return {}
        
        try:
            if settings.encryption_enabled:
                decrypted = self.cipher.decrypt(encrypted_data.encode())
                return json.loads(decrypted.decode())
            else:
                return json.loads(encrypted_data)
        except Exception as e:
            logger.error("Failed to decrypt data", error=str(e))
            return {}
    
    def _get_client_ip(self, request: Optional[Request]) -> Optional[str]:
        """Extract client IP address from request"""
        if not request:
            return None
        
        # Check for forwarded IP (behind proxy)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        return getattr(request.client, "host", None)
    
    def _log_audit(
        self,
        action: str,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status: str = "success",
        request: Optional[Request] = None
    ):
        """Log audit event"""
        if not settings.audit_logging:
            return
        
        audit_log = AuditLogModel(
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=json.dumps(details or {}),
            ip_address=self._get_client_ip(request),
            user_agent=request.headers.get("user-agent") if request else None,
            status=status
        )
        
        self.db.add(audit_log)
        self.db.commit()
    
    def _model_to_user(self, user_model: UserModel) -> User:
        """Convert database model to Pydantic model"""
        return User(
            id=user_model.id,
            username=user_model.username,
            email=user_model.email,
            full_name=user_model.full_name,
            is_active=user_model.is_active,
            is_superuser=user_model.is_superuser,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at,
            last_login=user_model.last_login,
            two_factor_enabled=user_model.two_factor_enabled,
            profile_data=self._decrypt_data(user_model.profile_data or "")
        )


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(lambda: None)  # Replace with your DB dependency
) -> User:
    """
    Dependency to get current authenticated user.
    
    This function extracts and validates the JWT token from the request
    and returns the current authenticated user.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    auth_manager = AuthManager(db)
    token_data = auth_manager.verify_token(credentials.credentials)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = auth_manager.get_user(token_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user account",
        )
    
    return user


def require_superuser(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to require superuser privileges"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser privileges required"
        )
    return current_user


def require_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to require active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user account"
        )
    return current_user
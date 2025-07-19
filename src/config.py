"""
Enterprise Configuration Management

This module provides comprehensive configuration management for the vessel
maintenance AI system, supporting multiple deployment environments,
multi-tenant architecture, and enterprise-grade security features.

Author: Fusionpact Technologies Inc.
Date: 2025-01-27
Version: 2.0.0
License: MIT License
"""

import os
from typing import Optional, List, Dict, Any
from pydantic import BaseSettings, Field, validator
from enum import Enum


class Environment(str, Enum):
    """Environment types for deployment configuration"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class DatabaseBackend(str, Enum):
    """Supported database backends"""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"


class AuthProvider(str, Enum):
    """Authentication provider types"""
    LOCAL = "local"
    LDAP = "ldap"
    OAUTH2 = "oauth2"
    SAML = "saml"


class CacheBackend(str, Enum):
    """Cache backend types"""
    MEMORY = "memory"
    REDIS = "redis"
    MEMCACHED = "memcached"


class Settings(BaseSettings):
    """
    Enterprise-grade configuration settings for the vessel maintenance AI system.
    
    This class defines all configuration parameters needed for enterprise
    deployment including multi-tenancy, security, scalability, and compliance.
    """
    
    # Application Settings
    app_name: str = Field(default="Vessel Maintenance AI System", env="APP_NAME")
    app_version: str = Field(default="2.0.0", env="APP_VERSION")
    environment: Environment = Field(default=Environment.DEVELOPMENT, env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=1, env="WORKERS")
    
    # Multi-Tenant Configuration
    multi_tenant_enabled: bool = Field(default=True, env="MULTI_TENANT_ENABLED")
    tenant_isolation_level: str = Field(default="database", env="TENANT_ISOLATION_LEVEL")  # database, schema, row
    default_tenant_id: str = Field(default="default", env="DEFAULT_TENANT_ID")
    max_tenants: int = Field(default=100, env="MAX_TENANTS")
    
    # Database Configuration
    database_backend: DatabaseBackend = Field(default=DatabaseBackend.SQLITE, env="DATABASE_BACKEND")
    database_url: str = Field(default="sqlite:///./data/vessel_maintenance.db", env="DATABASE_URL")
    database_pool_size: int = Field(default=20, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    database_pool_timeout: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    
    # PostgreSQL specific settings
    postgres_host: str = Field(default="localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    postgres_user: str = Field(default="vessel_admin", env="POSTGRES_USER")
    postgres_password: str = Field(default="", env="POSTGRES_PASSWORD")
    postgres_database: str = Field(default="vessel_maintenance", env="POSTGRES_DATABASE")
    
    # MySQL specific settings
    mysql_host: str = Field(default="localhost", env="MYSQL_HOST")
    mysql_port: int = Field(default=3306, env="MYSQL_PORT")
    mysql_user: str = Field(default="vessel_admin", env="MYSQL_USER")
    mysql_password: str = Field(default="", env="MYSQL_PASSWORD")
    mysql_database: str = Field(default="vessel_maintenance", env="MYSQL_DATABASE")
    
    # Authentication and Security
    auth_provider: AuthProvider = Field(default=AuthProvider.LOCAL, env="AUTH_PROVIDER")
    secret_key: str = Field(default="vessel-maintenance-secret-key-change-in-production", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # LDAP Configuration
    ldap_server: str = Field(default="", env="LDAP_SERVER")
    ldap_port: int = Field(default=389, env="LDAP_PORT")
    ldap_base_dn: str = Field(default="", env="LDAP_BASE_DN")
    ldap_user_dn: str = Field(default="", env="LDAP_USER_DN")
    ldap_password: str = Field(default="", env="LDAP_PASSWORD")
    
    # OAuth2 Configuration
    oauth2_client_id: str = Field(default="", env="OAUTH2_CLIENT_ID")
    oauth2_client_secret: str = Field(default="", env="OAUTH2_CLIENT_SECRET")
    oauth2_server_url: str = Field(default="", env="OAUTH2_SERVER_URL")
    
    # Rate Limiting
    rate_limiting_enabled: bool = Field(default=True, env="RATE_LIMITING_ENABLED")
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")
    rate_limit_per_day: int = Field(default=10000, env="RATE_LIMIT_PER_DAY")
    rate_limit_burst: int = Field(default=10, env="RATE_LIMIT_BURST")
    
    # Caching Configuration
    cache_backend: CacheBackend = Field(default=CacheBackend.MEMORY, env="CACHE_BACKEND")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")  # seconds
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_password: str = Field(default="", env="REDIS_PASSWORD")
    
    # Background Processing
    celery_broker_url: str = Field(default="redis://localhost:6379/1", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")
    batch_processing_enabled: bool = Field(default=True, env="BATCH_PROCESSING_ENABLED")
    max_batch_size: int = Field(default=100, env="MAX_BATCH_SIZE")
    
    # Security and Encryption
    encryption_enabled: bool = Field(default=True, env="ENCRYPTION_ENABLED")
    encryption_key: str = Field(default="", env="ENCRYPTION_KEY")
    data_at_rest_encryption: bool = Field(default=True, env="DATA_AT_REST_ENCRYPTION")
    ssl_enabled: bool = Field(default=False, env="SSL_ENABLED")
    ssl_cert_path: str = Field(default="", env="SSL_CERT_PATH")
    ssl_key_path: str = Field(default="", env="SSL_KEY_PATH")
    
    # CORS Configuration
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(default=["*"], env="CORS_ALLOW_METHODS")
    cors_allow_headers: List[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")
    
    # Monitoring and Observability
    monitoring_enabled: bool = Field(default=True, env="MONITORING_ENABLED")
    metrics_endpoint: str = Field(default="/metrics", env="METRICS_ENDPOINT")
    health_check_endpoint: str = Field(default="/health", env="HEALTH_CHECK_ENDPOINT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    structured_logging: bool = Field(default=True, env="STRUCTURED_LOGGING")
    
    # Real-time Notifications
    notifications_enabled: bool = Field(default=True, env="NOTIFICATIONS_ENABLED")
    websocket_enabled: bool = Field(default=True, env="WEBSOCKET_ENABLED")
    email_notifications: bool = Field(default=False, env="EMAIL_NOTIFICATIONS")
    sms_notifications: bool = Field(default=False, env="SMS_NOTIFICATIONS")
    
    # Email Configuration
    smtp_server: str = Field(default="", env="SMTP_SERVER")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: str = Field(default="", env="SMTP_USERNAME")
    smtp_password: str = Field(default="", env="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(default=True, env="SMTP_USE_TLS")
    
    # AI and ML Configuration
    custom_models_enabled: bool = Field(default=True, env="CUSTOM_MODELS_ENABLED")
    model_training_enabled: bool = Field(default=False, env="MODEL_TRAINING_ENABLED")
    model_storage_path: str = Field(default="./models", env="MODEL_STORAGE_PATH")
    auto_model_updates: bool = Field(default=False, env="AUTO_MODEL_UPDATES")
    
    # Analytics and Reporting
    advanced_analytics_enabled: bool = Field(default=True, env="ADVANCED_ANALYTICS_ENABLED")
    predictive_analytics: bool = Field(default=True, env="PREDICTIVE_ANALYTICS")
    trend_analysis: bool = Field(default=True, env="TREND_ANALYSIS")
    analytics_retention_days: int = Field(default=365, env="ANALYTICS_RETENTION_DAYS")
    
    # Compliance and Audit
    audit_logging: bool = Field(default=True, env="AUDIT_LOGGING")
    gdpr_compliance: bool = Field(default=True, env="GDPR_COMPLIANCE")
    data_retention_days: int = Field(default=2555, env="DATA_RETENTION_DAYS")  # 7 years
    audit_log_retention_days: int = Field(default=2555, env="AUDIT_LOG_RETENTION_DAYS")
    
    # Maritime Standards
    imo_compliance: bool = Field(default=True, env="IMO_COMPLIANCE")
    maritime_standards_validation: bool = Field(default=True, env="MARITIME_STANDARDS_VALIDATION")
    
    # File Upload Configuration
    max_file_size: int = Field(default=50 * 1024 * 1024, env="MAX_FILE_SIZE")  # 50MB
    allowed_file_types: List[str] = Field(
        default=[".txt", ".pdf", ".doc", ".docx", ".csv", ".json"],
        env="ALLOWED_FILE_TYPES"
    )
    
    # API Configuration
    api_prefix: str = Field(default="/api/v1", env="API_PREFIX")
    docs_url: str = Field(default="/docs", env="DOCS_URL")
    redoc_url: str = Field(default="/redoc", env="REDOC_URL")
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("cors_allow_methods", pre=True)
    def parse_cors_methods(cls, v):
        if isinstance(v, str):
            return [method.strip() for method in v.split(",")]
        return v
    
    @validator("cors_allow_headers", pre=True)
    def parse_cors_headers(cls, v):
        if isinstance(v, str):
            return [header.strip() for header in v.split(",")]
        return v
    
    @validator("allowed_file_types", pre=True)
    def parse_file_types(cls, v):
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v
    
    def get_database_url(self) -> str:
        """Get the appropriate database URL based on backend configuration"""
        if self.database_backend == DatabaseBackend.POSTGRESQL:
            return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database}"
        elif self.database_backend == DatabaseBackend.MYSQL:
            return f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        else:
            return self.database_url
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == Environment.DEVELOPMENT
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance"""
    return settings
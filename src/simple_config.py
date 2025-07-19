"""
Simplified Configuration Module

This module provides a basic configuration system without external dependencies
for validation and testing purposes.
"""

import os
from typing import Dict, Any, List
from enum import Enum


class Environment(str, Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class DatabaseBackend(str, Enum):
    """Database backends"""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"


class AuthProvider(str, Enum):
    """Authentication providers"""
    LOCAL = "local"
    LDAP = "ldap"
    OAUTH2 = "oauth2"
    SAML = "saml"


class CacheBackend(str, Enum):
    """Cache backends"""
    MEMORY = "memory"
    REDIS = "redis"
    MEMCACHED = "memcached"


class SimpleSettings:
    """Simplified settings class for enterprise features"""
    
    def __init__(self):
        # Application Settings
        self.app_name = os.getenv("APP_NAME", "Vessel Maintenance AI System - Enterprise")
        self.app_version = os.getenv("APP_VERSION", "2.0.0")
        self.environment = Environment(os.getenv("ENVIRONMENT", "development"))
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # Server Configuration
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", 8000))
        self.workers = int(os.getenv("WORKERS", 1))
        
        # Multi-Tenant Configuration
        self.multi_tenant_enabled = os.getenv("MULTI_TENANT_ENABLED", "true").lower() == "true"
        self.tenant_isolation_level = os.getenv("TENANT_ISOLATION_LEVEL", "database")
        self.default_tenant_id = os.getenv("DEFAULT_TENANT_ID", "default")
        self.max_tenants = int(os.getenv("MAX_TENANTS", 100))
        
        # Database Configuration
        self.database_backend = DatabaseBackend(os.getenv("DATABASE_BACKEND", "sqlite"))
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./data/vessel_maintenance.db")
        self.database_pool_size = int(os.getenv("DATABASE_POOL_SIZE", 20))
        self.database_max_overflow = int(os.getenv("DATABASE_MAX_OVERFLOW", 30))
        self.database_pool_timeout = int(os.getenv("DATABASE_POOL_TIMEOUT", 30))
        
        # Authentication and Security
        self.auth_provider = AuthProvider(os.getenv("AUTH_PROVIDER", "ldap"))
        self.secret_key = os.getenv("SECRET_KEY", "vessel-maintenance-secret-key-change-in-production")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
        self.refresh_token_expire_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
        
        # Rate Limiting
        self.rate_limiting_enabled = os.getenv("RATE_LIMITING_ENABLED", "true").lower() == "true"
        self.rate_limit_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", 60))
        self.rate_limit_per_hour = int(os.getenv("RATE_LIMIT_PER_HOUR", 1000))
        self.rate_limit_per_day = int(os.getenv("RATE_LIMIT_PER_DAY", 10000))
        self.rate_limit_burst = int(os.getenv("RATE_LIMIT_BURST", 10))
        
        # Caching Configuration
        self.cache_backend = CacheBackend(os.getenv("CACHE_BACKEND", "memory"))
        self.cache_ttl = int(os.getenv("CACHE_TTL", 3600))
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_password = os.getenv("REDIS_PASSWORD", "")
        
        # Security and Encryption
        self.encryption_enabled = os.getenv("ENCRYPTION_ENABLED", "true").lower() == "true"
        self.encryption_key = os.getenv("ENCRYPTION_KEY", "")
        self.data_at_rest_encryption = os.getenv("DATA_AT_REST_ENCRYPTION", "true").lower() == "true"
        self.ssl_enabled = os.getenv("SSL_ENABLED", "false").lower() == "true"
        
        # CORS Configuration
        cors_origins = os.getenv("CORS_ORIGINS", "*")
        self.cors_origins = [origin.strip() for origin in cors_origins.split(",")] if cors_origins != "*" else ["*"]
        self.cors_allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
        
        # Monitoring and Observability
        self.monitoring_enabled = os.getenv("MONITORING_ENABLED", "true").lower() == "true"
        self.metrics_endpoint = os.getenv("METRICS_ENDPOINT", "/metrics")
        self.health_check_endpoint = os.getenv("HEALTH_CHECK_ENDPOINT", "/health")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.structured_logging = os.getenv("STRUCTURED_LOGGING", "true").lower() == "true"
        
        # Real-time Notifications
        self.notifications_enabled = os.getenv("NOTIFICATIONS_ENABLED", "true").lower() == "true"
        self.websocket_enabled = os.getenv("WEBSOCKET_ENABLED", "true").lower() == "true"
        self.email_notifications = os.getenv("EMAIL_NOTIFICATIONS", "false").lower() == "true"
        self.sms_notifications = os.getenv("SMS_NOTIFICATIONS", "false").lower() == "true"
        
        # AI and ML Configuration
        self.custom_models_enabled = os.getenv("CUSTOM_MODELS_ENABLED", "true").lower() == "true"
        self.model_training_enabled = os.getenv("MODEL_TRAINING_ENABLED", "false").lower() == "true"
        self.model_storage_path = os.getenv("MODEL_STORAGE_PATH", "./models")
        self.auto_model_updates = os.getenv("AUTO_MODEL_UPDATES", "false").lower() == "true"
        
        # Analytics and Reporting
        self.advanced_analytics_enabled = os.getenv("ADVANCED_ANALYTICS_ENABLED", "true").lower() == "true"
        self.predictive_analytics = os.getenv("PREDICTIVE_ANALYTICS", "true").lower() == "true"
        self.trend_analysis = os.getenv("TREND_ANALYSIS", "true").lower() == "true"
        self.analytics_retention_days = int(os.getenv("ANALYTICS_RETENTION_DAYS", 365))
        
        # Compliance and Audit
        self.audit_logging = os.getenv("AUDIT_LOGGING", "true").lower() == "true"
        self.gdpr_compliance = os.getenv("GDPR_COMPLIANCE", "true").lower() == "true"
        self.data_retention_days = int(os.getenv("DATA_RETENTION_DAYS", 2555))
        self.audit_log_retention_days = int(os.getenv("AUDIT_LOG_RETENTION_DAYS", 2555))
        
        # Maritime Standards
        self.imo_compliance = os.getenv("IMO_COMPLIANCE", "true").lower() == "true"
        self.maritime_standards_validation = os.getenv("MARITIME_STANDARDS_VALIDATION", "true").lower() == "true"
        
        # API Configuration
        self.api_prefix = os.getenv("API_PREFIX", "/api/v1")
        self.docs_url = os.getenv("DOCS_URL", "/docs")
        self.redoc_url = os.getenv("REDOC_URL", "/redoc")
    
    def get_database_url(self) -> str:
        """Get the appropriate database URL based on backend configuration"""
        if self.database_backend == DatabaseBackend.POSTGRESQL:
            postgres_host = os.getenv("POSTGRES_HOST", "localhost")
            postgres_port = os.getenv("POSTGRES_PORT", "5432")
            postgres_user = os.getenv("POSTGRES_USER", "vessel_admin")
            postgres_password = os.getenv("POSTGRES_PASSWORD", "")
            postgres_database = os.getenv("POSTGRES_DATABASE", "vessel_maintenance")
            return f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_database}"
        elif self.database_backend == DatabaseBackend.MYSQL:
            mysql_host = os.getenv("MYSQL_HOST", "localhost")
            mysql_port = os.getenv("MYSQL_PORT", "3306")
            mysql_user = os.getenv("MYSQL_USER", "vessel_admin")
            mysql_password = os.getenv("MYSQL_PASSWORD", "")
            mysql_database = os.getenv("MYSQL_DATABASE", "vessel_maintenance")
            return f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
        else:
            return self.database_url
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == Environment.DEVELOPMENT
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary for inspection"""
        return {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "environment": self.environment.value,
            "multi_tenant_enabled": self.multi_tenant_enabled,
            "rate_limiting_enabled": self.rate_limiting_enabled,
            "monitoring_enabled": self.monitoring_enabled,
            "audit_logging": self.audit_logging,
            "encryption_enabled": self.encryption_enabled,
            "database_backend": self.database_backend.value,
            "auth_provider": self.auth_provider.value,
            "cache_backend": self.cache_backend.value,
            "advanced_analytics_enabled": self.advanced_analytics_enabled,
            "custom_models_enabled": self.custom_models_enabled,
            "gdpr_compliance": self.gdpr_compliance,
            "imo_compliance": self.imo_compliance
        }


# Global settings instance
settings = SimpleSettings()


def get_settings() -> SimpleSettings:
    """Get the global settings instance"""
    return settings


def validate_configuration() -> Dict[str, bool]:
    """Validate enterprise configuration"""
    config_status = {
        "multi_tenant_support": settings.multi_tenant_enabled,
        "advanced_analytics": settings.advanced_analytics_enabled,
        "api_rate_limiting": settings.rate_limiting_enabled,
        "custom_models": settings.custom_models_enabled,
        "enterprise_auth": settings.auth_provider != AuthProvider.LOCAL,
        "monitoring": settings.monitoring_enabled,
        "encryption": settings.encryption_enabled,
        "audit_logging": settings.audit_logging,
        "gdpr_compliance": settings.gdpr_compliance,
        "imo_compliance": settings.imo_compliance,
        "real_time_notifications": settings.notifications_enabled
    }
    
    return config_status


if __name__ == "__main__":
    print("=== Enterprise Configuration Validation ===")
    print(f"Application: {settings.app_name} v{settings.app_version}")
    print(f"Environment: {settings.environment.value}")
    print()
    
    config_status = validate_configuration()
    
    print("Enterprise Features Configuration:")
    for feature, enabled in config_status.items():
        status_text = "✅ Enabled" if enabled else "❌ Disabled"
        print(f"  {feature.replace('_', ' ').title()}: {status_text}")
    
    enabled_features = sum(config_status.values())
    total_features = len(config_status)
    
    print(f"\nSummary: {enabled_features}/{total_features} enterprise features enabled")
    
    if enabled_features >= total_features * 0.8:
        print("🎉 Enterprise configuration is properly set up!")
    else:
        print("⚠️  Consider enabling more enterprise features for production")
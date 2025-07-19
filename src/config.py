"""
Enterprise Configuration Module

This module provides comprehensive configuration management for enterprise features
including multi-tenancy, security, database settings, and feature flags.

Author: Fusionpact Technologies Inc.
Date: 2025-01-18
Version: 1.0.0
"""

import os
from typing import Dict, List, Optional, Any
from pydantic import BaseSettings, Field
from enum import Enum


class DatabaseType(str, Enum):
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"


class AuthenticationMethod(str, Enum):
    JWT = "jwt"
    API_KEY = "api_key"
    SSO = "sso"
    OAUTH2 = "oauth2"


class EncryptionLevel(str, Enum):
    NONE = "none"
    BASIC = "basic"
    ENTERPRISE = "enterprise"


class EnterpriseConfig(BaseSettings):
    """Enterprise configuration settings with comprehensive feature support."""
    
    # Application Settings
    app_name: str = "Vessel Maintenance AI System"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Multi-tenancy Configuration
    multi_tenant_enabled: bool = Field(default=True, env="MULTI_TENANT_ENABLED")
    tenant_isolation_level: str = Field(default="database", env="TENANT_ISOLATION_LEVEL")
    default_tenant_id: str = Field(default="default", env="DEFAULT_TENANT_ID")
    
    # Database Configuration
    database_type: DatabaseType = Field(default=DatabaseType.SQLITE, env="DATABASE_TYPE")
    database_url: str = Field(default="sqlite:///./data/vessel_ai.db", env="DATABASE_URL")
    database_pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # Authentication & Security
    secret_key: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    encryption_level: EncryptionLevel = Field(default=EncryptionLevel.ENTERPRISE, env="ENCRYPTION_LEVEL")
    encryption_key: Optional[str] = Field(default=None, env="ENCRYPTION_KEY")
    
    # Rate Limiting
    rate_limiting_enabled: bool = Field(default=True, env="RATE_LIMITING_ENABLED")
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=3600, env="RATE_LIMIT_WINDOW")
    
    # Caching Configuration
    cache_enabled: bool = Field(default=True, env="CACHE_ENABLED")
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")
    
    # Background Processing
    celery_broker_url: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")
    
    # Monitoring & Logging
    logging_level: str = Field(default="INFO", env="LOGGING_LEVEL")
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    prometheus_enabled: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    
    # Analytics & ML
    analytics_enabled: bool = Field(default=True, env="ANALYTICS_ENABLED")
    ml_model_cache_size: int = Field(default=100, env="ML_MODEL_CACHE_SIZE")
    prediction_batch_size: int = Field(default=50, env="PREDICTION_BATCH_SIZE")
    
    # Notifications
    notifications_enabled: bool = Field(default=True, env="NOTIFICATIONS_ENABLED")
    email_enabled: bool = Field(default=False, env="EMAIL_ENABLED")
    sms_enabled: bool = Field(default=False, env="SMS_ENABLED")
    webhook_enabled: bool = Field(default=True, env="WEBHOOK_ENABLED")
    
    # Compliance & Audit
    audit_logging_enabled: bool = Field(default=True, env="AUDIT_LOGGING_ENABLED")
    gdpr_compliance_enabled: bool = Field(default=True, env="GDPR_COMPLIANCE_ENABLED")
    data_retention_days: int = Field(default=2555, env="DATA_RETENTION_DAYS")  # 7 years
    
    # API Configuration
    api_version: str = Field(default="v1", env="API_VERSION")
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    api_documentation_enabled: bool = Field(default=True, env="API_DOCUMENTATION_ENABLED")
    
    # Performance & Scaling
    worker_processes: int = Field(default=4, env="WORKER_PROCESSES")
    max_concurrent_requests: int = Field(default=1000, env="MAX_CONCURRENT_REQUESTS")
    request_timeout: int = Field(default=300, env="REQUEST_TIMEOUT")
    
    # Feature Flags
    advanced_analytics_enabled: bool = Field(default=True, env="ADVANCED_ANALYTICS_ENABLED")
    custom_models_enabled: bool = Field(default=True, env="CUSTOM_MODELS_ENABLED")
    batch_processing_enabled: bool = Field(default=True, env="BATCH_PROCESSING_ENABLED")
    real_time_notifications_enabled: bool = Field(default=True, env="REAL_TIME_NOTIFICATIONS_ENABLED")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global configuration instance
config = EnterpriseConfig()


class FeatureFlags:
    """Feature flag management for enterprise features."""
    
    @staticmethod
    def is_multi_tenant_enabled() -> bool:
        return config.multi_tenant_enabled
    
    @staticmethod
    def is_advanced_analytics_enabled() -> bool:
        return config.advanced_analytics_enabled
    
    @staticmethod
    def is_custom_models_enabled() -> bool:
        return config.custom_models_enabled
    
    @staticmethod
    def is_batch_processing_enabled() -> bool:
        return config.batch_processing_enabled
    
    @staticmethod
    def is_real_time_notifications_enabled() -> bool:
        return config.real_time_notifications_enabled
    
    @staticmethod
    def is_audit_logging_enabled() -> bool:
        return config.audit_logging_enabled
    
    @staticmethod
    def is_gdpr_compliance_enabled() -> bool:
        return config.gdpr_compliance_enabled


class SecurityConfig:
    """Security configuration management."""
    
    @staticmethod
    def get_encryption_key() -> str:
        """Get encryption key with fallback to secret key."""
        return config.encryption_key or config.secret_key
    
    @staticmethod
    def is_encryption_enabled() -> bool:
        return config.encryption_level != EncryptionLevel.NONE
    
    @staticmethod
    def get_encryption_level() -> EncryptionLevel:
        return config.encryption_level


class DatabaseConfig:
    """Database configuration management."""
    
    @staticmethod
    def get_database_url() -> str:
        return config.database_url
    
    @staticmethod
    def get_database_type() -> DatabaseType:
        return config.database_type
    
    @staticmethod
    def get_pool_settings() -> Dict[str, Any]:
        return {
            "pool_size": config.database_pool_size,
            "max_overflow": config.database_max_overflow,
            "pool_pre_ping": True,
            "pool_recycle": 3600
        }


class CacheConfig:
    """Cache configuration management."""
    
    @staticmethod
    def is_cache_enabled() -> bool:
        return config.cache_enabled
    
    @staticmethod
    def get_redis_url() -> str:
        return config.redis_url
    
    @staticmethod
    def get_cache_ttl() -> int:
        return config.cache_ttl


class RateLimitConfig:
    """Rate limiting configuration."""
    
    @staticmethod
    def is_rate_limiting_enabled() -> bool:
        return config.rate_limiting_enabled
    
    @staticmethod
    def get_rate_limit_settings() -> Dict[str, int]:
        return {
            "requests": config.rate_limit_requests,
            "window": config.rate_limit_window
        }


# Enterprise feature configuration
ENTERPRISE_FEATURES = {
    "multi_tenant_architecture": {
        "enabled": True,
        "description": "Support for multiple fleet operators with data isolation",
        "components": ["tenant_management", "data_isolation", "tenant_routing"]
    },
    "advanced_analytics": {
        "enabled": True,
        "description": "Comprehensive reporting with trend analysis and predictive insights",
        "components": ["trend_analysis", "predictive_insights", "custom_reports"]
    },
    "api_rate_limiting": {
        "enabled": True,
        "description": "Configurable request throttling and quota management",
        "components": ["request_throttling", "quota_management", "rate_monitoring"]
    },
    "custom_classification_models": {
        "enabled": True,
        "description": "Ability to train and deploy domain-specific AI classifiers",
        "components": ["model_training", "model_deployment", "custom_weights"]
    },
    "integration_ready": {
        "enabled": True,
        "description": "RESTful APIs designed for seamless integration",
        "components": ["rest_api", "graphql", "webhooks", "sdk"]
    },
    "real_time_notifications": {
        "enabled": True,
        "description": "Configurable alert systems with multiple delivery channels",
        "components": ["email_alerts", "sms_alerts", "webhook_notifications", "push_notifications"]
    },
    "customization_options": {
        "enabled": True,
        "description": "Easily modify or extend AI classification rules and weights",
        "components": ["classification_patterns", "priority_thresholds", "alert_configurations"]
    },
    "database_backends": {
        "enabled": True,
        "description": "Support for SQLite (development) and PostgreSQL/MySQL (production)",
        "components": ["sqlite", "postgresql", "mysql", "connection_pooling"]
    },
    "authentication_systems": {
        "enabled": True,
        "description": "Ready for integration with enterprise SSO and RBAC systems",
        "components": ["jwt_auth", "api_keys", "sso_integration", "rbac"]
    },
    "workflow_integration": {
        "enabled": True,
        "description": "Compatible with popular workflow management platforms",
        "components": ["workflow_engines", "task_queues", "process_automation"]
    },
    "horizontal_scaling": {
        "enabled": True,
        "description": "Designed to scale across multiple server instances",
        "components": ["load_balancing", "stateless_design", "shared_state"]
    },
    "batch_processing": {
        "enabled": True,
        "description": "Support for bulk document processing with job queuing",
        "components": ["job_queues", "batch_processing", "progress_tracking"]
    },
    "caching_layer": {
        "enabled": True,
        "description": "Intelligent caching strategies for optimal performance",
        "components": ["redis_cache", "model_caching", "query_caching"]
    },
    "load_balancing": {
        "enabled": True,
        "description": "Compatible with standard load balancing and container orchestration",
        "components": ["health_checks", "service_discovery", "traffic_routing"]
    },
    "microservices_ready": {
        "enabled": True,
        "description": "Modular architecture suitable for microservices deployment",
        "components": ["service_decomposition", "api_gateway", "service_mesh"]
    },
    "high_availability": {
        "enabled": True,
        "description": "Built-in health monitoring and fault tolerance",
        "components": ["health_monitoring", "fault_tolerance", "auto_scaling"]
    },
    "data_encryption": {
        "enabled": True,
        "description": "End-to-end encryption for sensitive vessel data",
        "components": ["at_rest_encryption", "in_transit_encryption", "key_management"]
    },
    "audit_logging": {
        "enabled": True,
        "description": "Comprehensive audit trails for compliance requirements",
        "components": ["audit_trails", "compliance_logging", "data_lineage"]
    },
    "gdpr_compliance": {
        "enabled": True,
        "description": "Built-in privacy controls and data retention policies",
        "components": ["privacy_controls", "data_retention", "right_to_forget"]
    },
    "maritime_standards": {
        "enabled": True,
        "description": "Aligned with IMO and industry best practices",
        "components": ["imo_compliance", "marpol_standards", "industry_best_practices"]
    },
    "access_controls": {
        "enabled": True,
        "description": "Fine-grained permissions and role-based access",
        "components": ["rbac", "permission_management", "access_auditing"]
    }
}
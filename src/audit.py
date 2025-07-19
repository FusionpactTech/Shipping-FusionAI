"""
Audit Logging and Compliance Module

This module provides comprehensive audit logging and compliance features for enterprise
deployments, including audit trails, GDPR compliance, and data retention policies.

Author: Fusionpact Technologies Inc.
Date: 2025-01-18
Version: 1.0.0
"""

import json
import hashlib
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import logging
import asyncio
from dataclasses import dataclass, asdict

from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from .config import config, FeatureFlags
from .tenancy import get_current_tenant_id, get_current_tenant


class AuditEventType(str, Enum):
    # User Events
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    
    # Document Events
    DOCUMENT_UPLOADED = "document_uploaded"
    DOCUMENT_PROCESSED = "document_processed"
    DOCUMENT_DELETED = "document_deleted"
    DOCUMENT_EXPORTED = "document_exported"
    
    # System Events
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    CONFIGURATION_CHANGED = "configuration_changed"
    BACKUP_CREATED = "backup_created"
    
    # Security Events
    AUTHENTICATION_FAILED = "authentication_failed"
    AUTHORIZATION_FAILED = "authorization_failed"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    QUOTA_EXCEEDED = "quota_exceeded"
    
    # Data Events
    DATA_ACCESSED = "data_accessed"
    DATA_MODIFIED = "data_modified"
    DATA_DELETED = "data_deleted"
    DATA_EXPORTED = "data_exported"
    
    # API Events
    API_CALL = "api_call"
    API_ERROR = "api_error"
    API_RATE_LIMIT = "api_rate_limit"


class AuditSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DataRetentionPolicy(str, Enum):
    IMMEDIATE = "immediate"  # Delete immediately
    DAYS_7 = "7_days"
    DAYS_30 = "30_days"
    DAYS_90 = "90_days"
    DAYS_365 = "365_days"
    YEARS_7 = "7_years"  # Maritime compliance
    PERMANENT = "permanent"


class GDPRRight(str, Enum):
    ACCESS = "right_to_access"
    RECTIFICATION = "right_to_rectification"
    ERASURE = "right_to_erasure"
    PORTABILITY = "right_to_portability"
    RESTRICTION = "right_to_restriction"
    OBJECTION = "right_to_objection"


@dataclass
class AuditEvent:
    """Audit event record."""
    id: str
    tenant_id: str
    user_id: Optional[str]
    event_type: AuditEventType
    severity: AuditSeverity
    timestamp: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    resource_type: Optional[str]
    resource_id: Optional[str]
    action: str
    details: Dict[str, Any]
    outcome: str  # success, failure, partial
    session_id: Optional[str]
    request_id: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class DataSubject(BaseModel):
    """Data subject for GDPR compliance."""
    id: str
    tenant_id: str
    email: str
    name: Optional[str]
    consent_given: bool
    consent_date: Optional[datetime]
    data_retention_policy: DataRetentionPolicy
    created_at: datetime
    updated_at: datetime


class DataRetentionRule(BaseModel):
    """Data retention rule configuration."""
    id: str
    tenant_id: str
    data_type: str
    retention_policy: DataRetentionPolicy
    retention_period_days: int
    auto_delete: bool
    created_at: datetime
    updated_at: datetime


class GDPRRequest(BaseModel):
    """GDPR request record."""
    id: str
    tenant_id: str
    data_subject_id: str
    request_type: GDPRRight
    status: str  # pending, processing, completed, failed
    request_date: datetime
    completion_date: Optional[datetime]
    details: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class AuditLogger:
    """Comprehensive audit logging system."""
    
    def __init__(self):
        self.events: List[AuditEvent] = []
        self.logger = logging.getLogger(__name__)
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize audit database."""
        try:
            # Create audit tables if they don't exist
            engine = create_engine(config.database_url)
            with engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS audit_events (
                        id VARCHAR(255) PRIMARY KEY,
                        tenant_id VARCHAR(255) NOT NULL,
                        user_id VARCHAR(255),
                        event_type VARCHAR(100) NOT NULL,
                        severity VARCHAR(20) NOT NULL,
                        timestamp TIMESTAMP NOT NULL,
                        ip_address VARCHAR(45),
                        user_agent TEXT,
                        resource_type VARCHAR(100),
                        resource_id VARCHAR(255),
                        action VARCHAR(100) NOT NULL,
                        details JSON,
                        outcome VARCHAR(20) NOT NULL,
                        session_id VARCHAR(255),
                        request_id VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS data_subjects (
                        id VARCHAR(255) PRIMARY KEY,
                        tenant_id VARCHAR(255) NOT NULL,
                        email VARCHAR(255) NOT NULL,
                        name VARCHAR(255),
                        consent_given BOOLEAN DEFAULT FALSE,
                        consent_date TIMESTAMP,
                        data_retention_policy VARCHAR(50) DEFAULT '7_years',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS gdpr_requests (
                        id VARCHAR(255) PRIMARY KEY,
                        tenant_id VARCHAR(255) NOT NULL,
                        data_subject_id VARCHAR(255) NOT NULL,
                        request_type VARCHAR(50) NOT NULL,
                        status VARCHAR(20) DEFAULT 'pending',
                        request_date TIMESTAMP NOT NULL,
                        completion_date TIMESTAMP,
                        details JSON,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to initialize audit database: {e}")
    
    def log_event(self, event_type: AuditEventType, action: str, details: Dict[str, Any],
                  severity: AuditSeverity = AuditSeverity.MEDIUM, outcome: str = "success",
                  user_id: Optional[str] = None, resource_type: Optional[str] = None,
                  resource_id: Optional[str] = None, ip_address: Optional[str] = None,
                  user_agent: Optional[str] = None, session_id: Optional[str] = None,
                  request_id: Optional[str] = None) -> str:
        """Log an audit event."""
        if not FeatureFlags.is_audit_logging_enabled():
            return ""
        
        tenant_id = get_current_tenant_id() or "default"
        
        event = AuditEvent(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            user_id=user_id,
            event_type=event_type,
            severity=severity,
            timestamp=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            details=details,
            outcome=outcome,
            session_id=session_id,
            request_id=request_id
        )
        
        # Store in memory
        self.events.append(event)
        
        # Store in database
        self._store_event(event)
        
        # Log to file
        self._log_to_file(event)
        
        return event.id
    
    def _store_event(self, event: AuditEvent) -> None:
        """Store event in database."""
        try:
            engine = create_engine(config.database_url)
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO audit_events (
                        id, tenant_id, user_id, event_type, severity, timestamp,
                        ip_address, user_agent, resource_type, resource_id,
                        action, details, outcome, session_id, request_id
                    ) VALUES (
                        :id, :tenant_id, :user_id, :event_type, :severity, :timestamp,
                        :ip_address, :user_agent, :resource_type, :resource_id,
                        :action, :details, :outcome, :session_id, :request_id
                    )
                """), {
                    "id": event.id,
                    "tenant_id": event.tenant_id,
                    "user_id": event.user_id,
                    "event_type": event.event_type.value,
                    "severity": event.severity.value,
                    "timestamp": event.timestamp,
                    "ip_address": event.ip_address,
                    "user_agent": event.user_agent,
                    "resource_type": event.resource_type,
                    "resource_id": event.resource_id,
                    "action": event.action,
                    "details": json.dumps(event.details),
                    "outcome": event.outcome,
                    "session_id": event.session_id,
                    "request_id": event.request_id
                })
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to store audit event: {e}")
    
    def _log_to_file(self, event: AuditEvent) -> None:
        """Log event to file."""
        try:
            log_entry = {
                "timestamp": event.timestamp.isoformat(),
                "event_id": event.id,
                "tenant_id": event.tenant_id,
                "user_id": event.user_id,
                "event_type": event.event_type.value,
                "severity": event.severity.value,
                "action": event.action,
                "outcome": event.outcome,
                "details": event.details
            }
            
            with open("logs/audit.log", "a") as f:
                f.write(json.dumps(log_entry) + "\n")
                
        except Exception as e:
            self.logger.error(f"Failed to log audit event to file: {e}")
    
    def get_events(self, tenant_id: Optional[str] = None, event_type: Optional[AuditEventType] = None,
                   severity: Optional[AuditSeverity] = None, start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None, limit: int = 100) -> List[AuditEvent]:
        """Get audit events with filters."""
        events = self.events
        
        if tenant_id:
            events = [e for e in events if e.tenant_id == tenant_id]
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if severity:
            events = [e for e in events if e.severity == severity]
        
        if start_date:
            events = [e for e in events if e.timestamp >= start_date]
        
        if end_date:
            events = [e for e in events if e.timestamp <= end_date]
        
        return sorted(events, key=lambda x: x.timestamp, reverse=True)[:limit]


class GDPRCompliance:
    """GDPR compliance management."""
    
    def __init__(self):
        self.data_subjects: Dict[str, DataSubject] = {}
        self.retention_rules: Dict[str, DataRetentionRule] = {}
        self.gdpr_requests: Dict[str, GDPRRequest] = {}
        self.logger = logging.getLogger(__name__)
        self._load_default_retention_rules()
    
    def _load_default_retention_rules(self) -> None:
        """Load default data retention rules."""
        rules = [
            DataRetentionRule(
                id="audit_logs",
                tenant_id="default",
                data_type="audit_logs",
                retention_policy=DataRetentionPolicy.YEARS_7,
                retention_period_days=2555,
                auto_delete=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            DataRetentionRule(
                id="user_data",
                tenant_id="default",
                data_type="user_data",
                retention_policy=DataRetentionPolicy.YEARS_7,
                retention_period_days=2555,
                auto_delete=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            DataRetentionRule(
                id="documents",
                tenant_id="default",
                data_type="documents",
                retention_policy=DataRetentionPolicy.YEARS_7,
                retention_period_days=2555,
                auto_delete=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            DataRetentionRule(
                id="temporary_data",
                tenant_id="default",
                data_type="temporary_data",
                retention_policy=DataRetentionPolicy.DAYS_30,
                retention_period_days=30,
                auto_delete=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]
        
        for rule in rules:
            self.retention_rules[rule.id] = rule
    
    def register_data_subject(self, email: str, name: Optional[str] = None,
                            consent_given: bool = False) -> DataSubject:
        """Register a new data subject."""
        tenant_id = get_current_tenant_id() or "default"
        
        data_subject = DataSubject(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            email=email,
            name=name,
            consent_given=consent_given,
            consent_date=datetime.utcnow() if consent_given else None,
            data_retention_policy=DataRetentionPolicy.YEARS_7,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.data_subjects[data_subject.id] = data_subject
        self._store_data_subject(data_subject)
        
        return data_subject
    
    def update_consent(self, data_subject_id: str, consent_given: bool) -> Optional[DataSubject]:
        """Update data subject consent."""
        data_subject = self.data_subjects.get(data_subject_id)
        if not data_subject:
            return None
        
        data_subject.consent_given = consent_given
        data_subject.consent_date = datetime.utcnow() if consent_given else None
        data_subject.updated_at = datetime.utcnow()
        
        self._store_data_subject(data_subject)
        
        return data_subject
    
    def submit_gdpr_request(self, data_subject_id: str, request_type: GDPRRight,
                          details: Optional[Dict[str, Any]] = None) -> GDPRRequest:
        """Submit a GDPR request."""
        tenant_id = get_current_tenant_id() or "default"
        
        gdpr_request = GDPRRequest(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            data_subject_id=data_subject_id,
            request_type=request_type,
            status="pending",
            request_date=datetime.utcnow(),
            details=details or {},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.gdpr_requests[gdpr_request.id] = gdpr_request
        self._store_gdpr_request(gdpr_request)
        
        return gdpr_request
    
    def process_gdpr_request(self, request_id: str, status: str = "completed",
                           completion_details: Optional[Dict[str, Any]] = None) -> Optional[GDPRRequest]:
        """Process a GDPR request."""
        gdpr_request = self.gdpr_requests.get(request_id)
        if not gdpr_request:
            return None
        
        gdpr_request.status = status
        gdpr_request.completion_date = datetime.utcnow() if status == "completed" else None
        gdpr_request.details.update(completion_details or {})
        gdpr_request.updated_at = datetime.utcnow()
        
        self._store_gdpr_request(gdpr_request)
        
        return gdpr_request
    
    def get_data_subject_data(self, data_subject_id: str) -> Dict[str, Any]:
        """Get all data for a data subject (Right to Access)."""
        data_subject = self.data_subjects.get(data_subject_id)
        if not data_subject:
            return {}
        
        # This would collect all data related to the data subject
        # For now, return basic information
        return {
            "data_subject": data_subject.dict(),
            "gdpr_requests": [
                req.dict() for req in self.gdpr_requests.values()
                if req.data_subject_id == data_subject_id
            ],
            "audit_events": []  # Would be populated from audit logger
        }
    
    def delete_data_subject_data(self, data_subject_id: str) -> bool:
        """Delete all data for a data subject (Right to Erasure)."""
        data_subject = self.data_subjects.get(data_subject_id)
        if not data_subject:
            return False
        
        # Mark for deletion
        data_subject.data_retention_policy = DataRetentionPolicy.IMMEDIATE
        data_subject.updated_at = datetime.utcnow()
        
        # This would trigger actual data deletion
        self._delete_data_subject_data(data_subject_id)
        
        return True
    
    def _delete_data_subject_data(self, data_subject_id: str) -> None:
        """Actually delete data subject data."""
        # This would delete all data related to the data subject
        # Implementation depends on data storage
        self.logger.info(f"Deleting data for subject: {data_subject_id}")
    
    def _store_data_subject(self, data_subject: DataSubject) -> None:
        """Store data subject in database."""
        try:
            engine = create_engine(config.database_url)
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT OR REPLACE INTO data_subjects (
                        id, tenant_id, email, name, consent_given, consent_date,
                        data_retention_policy, created_at, updated_at
                    ) VALUES (
                        :id, :tenant_id, :email, :name, :consent_given, :consent_date,
                        :data_retention_policy, :created_at, :updated_at
                    )
                """), {
                    "id": data_subject.id,
                    "tenant_id": data_subject.tenant_id,
                    "email": data_subject.email,
                    "name": data_subject.name,
                    "consent_given": data_subject.consent_given,
                    "consent_date": data_subject.consent_date,
                    "data_retention_policy": data_subject.data_retention_policy.value,
                    "created_at": data_subject.created_at,
                    "updated_at": data_subject.updated_at
                })
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to store data subject: {e}")
    
    def _store_gdpr_request(self, gdpr_request: GDPRRequest) -> None:
        """Store GDPR request in database."""
        try:
            engine = create_engine(config.database_url)
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT OR REPLACE INTO gdpr_requests (
                        id, tenant_id, data_subject_id, request_type, status,
                        request_date, completion_date, details, created_at, updated_at
                    ) VALUES (
                        :id, :tenant_id, :data_subject_id, :request_type, :status,
                        :request_date, :completion_date, :details, :created_at, :updated_at
                    )
                """), {
                    "id": gdpr_request.id,
                    "tenant_id": gdpr_request.tenant_id,
                    "data_subject_id": gdpr_request.data_subject_id,
                    "request_type": gdpr_request.request_type.value,
                    "status": gdpr_request.status,
                    "request_date": gdpr_request.request_date,
                    "completion_date": gdpr_request.completion_date,
                    "details": json.dumps(gdpr_request.details),
                    "created_at": gdpr_request.created_at,
                    "updated_at": gdpr_request.updated_at
                })
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to store GDPR request: {e}")


class DataRetentionManager:
    """Data retention policy management."""
    
    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger
        self.logger = logging.getLogger(__name__)
    
    def apply_retention_policies(self) -> Dict[str, int]:
        """Apply data retention policies."""
        if not FeatureFlags.is_gdpr_compliance_enabled():
            return {}
        
        deletion_counts = {}
        
        try:
            engine = create_engine(config.database_url)
            with engine.connect() as conn:
                # Delete audit events older than retention period
                result = conn.execute(text("""
                    DELETE FROM audit_events 
                    WHERE timestamp < datetime('now', '-7 years')
                """))
                deletion_counts["audit_events"] = result.rowcount
                
                # Delete temporary data older than 30 days
                # This would be implemented based on actual data types
                deletion_counts["temporary_data"] = 0
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to apply retention policies: {e}")
        
        return deletion_counts
    
    def get_retention_summary(self) -> Dict[str, Any]:
        """Get data retention summary."""
        try:
            engine = create_engine(config.database_url)
            with engine.connect() as conn:
                # Get audit events count by age
                result = conn.execute(text("""
                    SELECT 
                        CASE 
                            WHEN timestamp > datetime('now', '-1 day') THEN 'last_24h'
                            WHEN timestamp > datetime('now', '-7 days') THEN 'last_7_days'
                            WHEN timestamp > datetime('now', '-30 days') THEN 'last_30_days'
                            WHEN timestamp > datetime('now', '-1 year') THEN 'last_year'
                            ELSE 'older'
                        END as age_group,
                        COUNT(*) as count
                    FROM audit_events
                    GROUP BY age_group
                """))
                
                age_distribution = {row[0]: row[1] for row in result}
                
                return {
                    "total_audit_events": sum(age_distribution.values()),
                    "age_distribution": age_distribution,
                    "retention_policies": {
                        "audit_events": "7_years",
                        "user_data": "7_years",
                        "documents": "7_years",
                        "temporary_data": "30_days"
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get retention summary: {e}")
            return {}


# Global instances
audit_logger = AuditLogger()
gdpr_compliance = GDPRCompliance()
data_retention_manager = DataRetentionManager(audit_logger)


def log_audit_event(event_type: AuditEventType, action: str, details: Dict[str, Any],
                   severity: AuditSeverity = AuditSeverity.MEDIUM, outcome: str = "success",
                   **kwargs) -> str:
    """Helper function to log audit events."""
    return audit_logger.log_event(
        event_type=event_type,
        action=action,
        details=details,
        severity=severity,
        outcome=outcome,
        **kwargs
    )


def require_audit_logging(func):
    """Decorator to automatically log function calls."""
    def wrapper(*args, **kwargs):
        # Log function call
        log_audit_event(
            event_type=AuditEventType.API_CALL,
            action=f"{func.__module__}.{func.__name__}",
            details={"args": str(args), "kwargs": str(kwargs)},
            severity=AuditSeverity.LOW
        )
        
        try:
            result = func(*args, **kwargs)
            # Log successful completion
            log_audit_event(
                event_type=AuditEventType.API_CALL,
                action=f"{func.__module__}.{func.__name__}",
                details={"result": "success"},
                severity=AuditSeverity.LOW,
                outcome="success"
            )
            return result
        except Exception as e:
            # Log error
            log_audit_event(
                event_type=AuditEventType.API_ERROR,
                action=f"{func.__module__}.{func.__name__}",
                details={"error": str(e)},
                severity=AuditSeverity.HIGH,
                outcome="failure"
            )
            raise
    
    return wrapper
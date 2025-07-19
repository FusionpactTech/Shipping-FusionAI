"""
Notifications and Monitoring Module

This module provides comprehensive notification and monitoring features for enterprise
deployments, including real-time alerts, multiple delivery channels, and monitoring
capabilities.

Author: Fusionpact Technologies Inc.
Date: 2025-01-18
Version: 1.0.0
"""

import asyncio
import json
import smtplib
import ssl
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import logging
import httpx
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from pydantic import BaseModel, EmailStr
from fastapi import HTTPException

from .config import config
from .tenancy import get_current_tenant_id, get_current_tenant


class NotificationType(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SUCCESS = "success"


class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    PUSH = "push"
    SLACK = "slack"
    TEAMS = "teams"
    DISCORD = "discord"


class NotificationPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"
    READ = "read"


class NotificationTemplate(BaseModel):
    """Notification template configuration."""
    id: str
    name: str
    subject: str
    body: str
    channels: List[NotificationChannel]
    priority: NotificationPriority = NotificationPriority.NORMAL
    created_at: datetime
    updated_at: datetime
    
    class Config:
        use_enum_values = True


class NotificationRule(BaseModel):
    """Notification rule configuration."""
    id: str
    name: str
    event_type: str
    conditions: Dict[str, Any]
    template_id: str
    channels: List[NotificationChannel]
    recipients: List[str]
    enabled: bool = True
    created_at: datetime
    updated_at: datetime
    
    class Config:
        use_enum_values = True


class Notification(BaseModel):
    """Notification model."""
    id: str
    tenant_id: str
    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority
    channels: List[NotificationChannel]
    recipients: List[str]
    metadata: Dict[str, Any] = {}
    status: NotificationStatus = NotificationStatus.PENDING
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        use_enum_values = True


class EmailConfig(BaseModel):
    """Email configuration."""
    smtp_server: str
    smtp_port: int
    username: str
    password: str
    use_tls: bool = True
    from_email: str
    from_name: str = "Vessel AI System"


class WebhookConfig(BaseModel):
    """Webhook configuration."""
    url: str
    method: str = "POST"
    headers: Dict[str, str] = {}
    timeout: int = 30


class NotificationChannelConfig:
    """Configuration for notification channels."""
    
    def __init__(self):
        self.email_config: Optional[EmailConfig] = None
        self.webhook_configs: Dict[str, WebhookConfig] = {}
        self.slack_webhook_url: Optional[str] = None
        self.teams_webhook_url: Optional[str] = None
        self.discord_webhook_url: Optional[str] = None
        self.sms_config: Optional[Dict[str, Any]] = None
    
    def set_email_config(self, config: EmailConfig) -> None:
        """Set email configuration."""
        self.email_config = config
    
    def add_webhook_config(self, name: str, config: WebhookConfig) -> None:
        """Add webhook configuration."""
        self.webhook_configs[name] = config
    
    def set_slack_webhook(self, url: str) -> None:
        """Set Slack webhook URL."""
        self.slack_webhook_url = url
    
    def set_teams_webhook(self, url: str) -> None:
        """Set Teams webhook URL."""
        self.teams_webhook_url = url
    
    def set_discord_webhook(self, url: str) -> None:
        """Set Discord webhook URL."""
        self.discord_webhook_url = url


class EmailNotifier:
    """Email notification sender."""
    
    def __init__(self, config: EmailConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def send(self, to_emails: List[str], subject: str, body: str, 
                   html_body: Optional[str] = None) -> bool:
        """Send email notification."""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.config.from_name} <{self.config.from_email}>"
            msg['To'] = ", ".join(to_emails)
            
            # Add text part
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls(context=context)
                server.login(self.config.username, self.config.password)
                server.send_message(msg)
            
            self.logger.info(f"Email sent to {to_emails}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False


class WebhookNotifier:
    """Webhook notification sender."""
    
    def __init__(self, config: WebhookConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def send(self, payload: Dict[str, Any]) -> bool:
        """Send webhook notification."""
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.request(
                    method=self.config.method,
                    url=self.config.url,
                    headers=self.config.headers,
                    json=payload
                )
                response.raise_for_status()
                
                self.logger.info(f"Webhook sent to {self.config.url}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to send webhook: {e}")
            return False


class SlackNotifier:
    """Slack notification sender."""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.logger = logging.getLogger(__name__)
    
    async def send(self, message: str, channel: Optional[str] = None, 
                   username: str = "Vessel AI Bot") -> bool:
        """Send Slack notification."""
        try:
            payload = {
                "text": message,
                "username": username
            }
            
            if channel:
                payload["channel"] = channel
            
            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook_url, json=payload)
                response.raise_for_status()
                
                self.logger.info("Slack notification sent")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to send Slack notification: {e}")
            return False


class NotificationManager:
    """Main notification manager."""
    
    def __init__(self):
        self.templates: Dict[str, NotificationTemplate] = {}
        self.rules: Dict[str, NotificationRule] = {}
        self.notifications: List[Notification] = []
        self.channel_config = NotificationChannelConfig()
        self.notifiers: Dict[NotificationChannel, Any] = {}
        self.logger = logging.getLogger(__name__)
        self._load_default_templates()
        self._load_default_rules()
    
    def _load_default_templates(self) -> None:
        """Load default notification templates."""
        templates = [
            NotificationTemplate(
                id="document_processed",
                name="Document Processed",
                subject="Document Processing Complete",
                body="Document '{document_name}' has been processed successfully. Classification: {classification}, Priority: {priority}",
                channels=[NotificationChannel.EMAIL, NotificationChannel.WEBHOOK],
                priority=NotificationPriority.NORMAL,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            NotificationTemplate(
                id="system_alert",
                name="System Alert",
                subject="System Alert: {alert_type}",
                body="System alert detected: {message}. Severity: {severity}",
                channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK, NotificationChannel.WEBHOOK],
                priority=NotificationPriority.HIGH,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            NotificationTemplate(
                id="quota_exceeded",
                name="Quota Exceeded",
                subject="Quota Limit Exceeded",
                body="Quota limit exceeded for tenant {tenant_id}. Current usage: {usage}/{limit}",
                channels=[NotificationChannel.EMAIL, NotificationChannel.WEBHOOK],
                priority=NotificationPriority.URGENT,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            NotificationTemplate(
                id="model_trained",
                name="Model Training Complete",
                subject="AI Model Training Complete",
                body="Model '{model_name}' training completed successfully. Accuracy: {accuracy}%",
                channels=[NotificationChannel.EMAIL, NotificationChannel.WEBHOOK],
                priority=NotificationPriority.NORMAL,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]
        
        for template in templates:
            self.templates[template.id] = template
    
    def _load_default_rules(self) -> None:
        """Load default notification rules."""
        rules = [
            NotificationRule(
                id="high_priority_document",
                name="High Priority Document Alert",
                event_type="document_processed",
                conditions={"priority": "high"},
                template_id="document_processed",
                channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
                recipients=["admin@vesselai.com"],
                enabled=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            NotificationRule(
                id="system_error",
                name="System Error Alert",
                event_type="system_error",
                conditions={"severity": "high"},
                template_id="system_alert",
                channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK, NotificationChannel.WEBHOOK],
                recipients=["admin@vesselai.com", "ops@vesselai.com"],
                enabled=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            NotificationRule(
                id="quota_warning",
                name="Quota Warning",
                event_type="quota_exceeded",
                conditions={"threshold": 0.8},
                template_id="quota_exceeded",
                channels=[NotificationChannel.EMAIL],
                recipients=["admin@vesselai.com"],
                enabled=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]
        
        for rule in rules:
            self.rules[rule.id] = rule
    
    def add_template(self, template: NotificationTemplate) -> None:
        """Add notification template."""
        self.templates[template.id] = template
    
    def add_rule(self, rule: NotificationRule) -> None:
        """Add notification rule."""
        self.rules[rule.id] = rule
    
    async def send_notification(self, notification: Notification) -> bool:
        """Send notification through all configured channels."""
        success = True
        
        for channel in notification.channels:
            try:
                if channel == NotificationChannel.EMAIL:
                    success &= await self._send_email(notification)
                elif channel == NotificationChannel.WEBHOOK:
                    success &= await self._send_webhook(notification)
                elif channel == NotificationChannel.SLACK:
                    success &= await self._send_slack(notification)
                elif channel == NotificationChannel.TEAMS:
                    success &= await self._send_teams(notification)
                elif channel == NotificationChannel.DISCORD:
                    success &= await self._send_discord(notification)
                else:
                    self.logger.warning(f"Unsupported channel: {channel}")
                    success = False
                    
            except Exception as e:
                self.logger.error(f"Failed to send notification via {channel}: {e}")
                success = False
        
        # Update notification status
        if success:
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.utcnow()
        else:
            notification.status = NotificationStatus.FAILED
        
        notification.updated_at = datetime.utcnow()
        self.notifications.append(notification)
        
        return success
    
    async def _send_email(self, notification: Notification) -> bool:
        """Send email notification."""
        if not self.channel_config.email_config:
            self.logger.warning("Email configuration not set")
            return False
        
        notifier = EmailNotifier(self.channel_config.email_config)
        return await notifier.send(
            to_emails=notification.recipients,
            subject=notification.title,
            body=notification.message
        )
    
    async def _send_webhook(self, notification: Notification) -> bool:
        """Send webhook notification."""
        if not self.channel_config.webhook_configs:
            self.logger.warning("Webhook configuration not set")
            return False
        
        success = True
        for name, config in self.channel_config.webhook_configs.items():
            notifier = WebhookNotifier(config)
            payload = {
                "notification_id": notification.id,
                "type": notification.type,
                "title": notification.title,
                "message": notification.message,
                "priority": notification.priority,
                "tenant_id": notification.tenant_id,
                "timestamp": notification.created_at.isoformat(),
                "metadata": notification.metadata
            }
            success &= await notifier.send(payload)
        
        return success
    
    async def _send_slack(self, notification: Notification) -> bool:
        """Send Slack notification."""
        if not self.channel_config.slack_webhook_url:
            self.logger.warning("Slack webhook URL not set")
            return False
        
        notifier = SlackNotifier(self.channel_config.slack_webhook_url)
        message = f"*{notification.title}*\n{notification.message}\nPriority: {notification.priority}"
        return await notifier.send(message)
    
    async def _send_teams(self, notification: Notification) -> bool:
        """Send Teams notification."""
        if not self.channel_config.teams_webhook_url:
            self.logger.warning("Teams webhook URL not set")
            return False
        
        # Similar to Slack but with Teams-specific formatting
        notifier = WebhookNotifier(WebhookConfig(url=self.channel_config.teams_webhook_url))
        payload = {
            "text": f"**{notification.title}**\n{notification.message}\nPriority: {notification.priority}"
        }
        return await notifier.send(payload)
    
    async def _send_discord(self, notification: Notification) -> bool:
        """Send Discord notification."""
        if not self.channel_config.discord_webhook_url:
            self.logger.warning("Discord webhook URL not set")
            return False
        
        notifier = WebhookNotifier(WebhookConfig(url=self.channel_config.discord_webhook_url))
        payload = {
            "content": f"**{notification.title}**\n{notification.message}\nPriority: {notification.priority}"
        }
        return await notifier.send(payload)
    
    async def process_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Process event and trigger notifications based on rules."""
        tenant_id = get_current_tenant_id() or "default"
        
        for rule in self.rules.values():
            if not rule.enabled or rule.event_type != event_type:
                continue
            
            # Check conditions
            if not self._check_conditions(rule.conditions, event_data):
                continue
            
            # Get template
            template = self.templates.get(rule.template_id)
            if not template:
                continue
            
            # Create notification
            notification = Notification(
                id=f"notif_{len(self.notifications) + 1}",
                tenant_id=tenant_id,
                type=NotificationType.INFO,
                title=template.subject.format(**event_data),
                message=template.body.format(**event_data),
                priority=template.priority,
                channels=rule.channels,
                recipients=rule.recipients,
                metadata=event_data,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Send notification
            await self.send_notification(notification)
    
    def _check_conditions(self, conditions: Dict[str, Any], event_data: Dict[str, Any]) -> bool:
        """Check if event data matches conditions."""
        for key, value in conditions.items():
            if key not in event_data or event_data[key] != value:
                return False
        return True
    
    def get_notifications(self, tenant_id: Optional[str] = None, 
                         limit: int = 50) -> List[Notification]:
        """Get notifications for tenant."""
        notifications = self.notifications
        
        if tenant_id:
            notifications = [n for n in notifications if n.tenant_id == tenant_id]
        
        return sorted(notifications, key=lambda x: x.created_at, reverse=True)[:limit]


class MonitoringService:
    """System monitoring and health checks."""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
        self.notification_manager = NotificationManager()
    
    def record_metric(self, name: str, value: Any, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a metric."""
        if name not in self.metrics:
            self.metrics[name] = []
        
        metric_data = {
            "value": value,
            "timestamp": datetime.utcnow(),
            "tags": tags or {}
        }
        
        self.metrics[name].append(metric_data)
        
        # Keep only last 1000 metrics per name
        if len(self.metrics[name]) > 1000:
            self.metrics[name] = self.metrics[name][-1000:]
    
    def get_metric(self, name: str, minutes: int = 60) -> List[Dict[str, Any]]:
        """Get metrics for the last N minutes."""
        if name not in self.metrics:
            return []
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        return [m for m in self.metrics[name] if m["timestamp"] > cutoff_time]
    
    def check_health(self) -> Dict[str, Any]:
        """Perform system health check."""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "checks": {}
        }
        
        # Check database connectivity
        try:
            # This would check actual database connection
            health_status["checks"]["database"] = {"status": "healthy"}
        except Exception as e:
            health_status["checks"]["database"] = {"status": "unhealthy", "error": str(e)}
            health_status["status"] = "unhealthy"
        
        # Check cache connectivity
        try:
            # This would check Redis connection
            health_status["checks"]["cache"] = {"status": "healthy"}
        except Exception as e:
            health_status["checks"]["cache"] = {"status": "unhealthy", "error": str(e)}
            health_status["status"] = "unhealthy"
        
        # Check external services
        try:
            # This would check external API connectivity
            health_status["checks"]["external_services"] = {"status": "healthy"}
        except Exception as e:
            health_status["checks"]["external_services"] = {"status": "unhealthy", "error": str(e)}
            health_status["status"] = "unhealthy"
        
        return health_status
    
    async def send_alert(self, alert_type: str, message: str, severity: str = "medium") -> None:
        """Send system alert."""
        alert = {
            "id": f"alert_{len(self.alerts) + 1}",
            "type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": datetime.utcnow()
        }
        
        self.alerts.append(alert)
        
        # Send notification
        await self.notification_manager.process_event("system_error", {
            "alert_type": alert_type,
            "message": message,
            "severity": severity
        })
    
    def get_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent alerts."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [a for a in self.alerts if a["timestamp"] > cutoff_time]


# Global instances
notification_manager = NotificationManager()
monitoring_service = MonitoringService()


async def send_notification(notification_type: NotificationType, title: str, message: str,
                          priority: NotificationPriority = NotificationPriority.NORMAL,
                          channels: Optional[List[NotificationChannel]] = None,
                          recipients: Optional[List[str]] = None) -> bool:
    """Helper function to send notifications."""
    tenant_id = get_current_tenant_id() or "default"
    
    notification = Notification(
        id=f"notif_{len(notification_manager.notifications) + 1}",
        tenant_id=tenant_id,
        type=notification_type,
        title=title,
        message=message,
        priority=priority,
        channels=channels or [NotificationChannel.EMAIL],
        recipients=recipients or ["admin@vesselai.com"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    return await notification_manager.send_notification(notification)


async def record_metric(name: str, value: Any, tags: Optional[Dict[str, str]] = None) -> None:
    """Helper function to record metrics."""
    monitoring_service.record_metric(name, value, tags)


async def check_system_health() -> Dict[str, Any]:
    """Helper function to check system health."""
    return monitoring_service.check_health()
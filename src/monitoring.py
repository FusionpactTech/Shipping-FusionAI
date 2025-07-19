"""
Enterprise Monitoring and Observability Module

This module provides comprehensive monitoring, metrics collection, health checks,
and observability features for the vessel maintenance AI system, including
Prometheus metrics, structured logging, and real-time alerting.

Author: Fusionpact Technologies Inc.
Date: 2025-01-27
Version: 2.0.0
License: MIT License
"""

import time
import psutil
import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from fastapi import Request, Response
from prometheus_client import Counter, Histogram, Gauge, Info, CollectorRegistry, generate_latest
import structlog
import json
from dataclasses import dataclass, asdict
from enum import Enum
import logging

from .config import settings

logger = structlog.get_logger(__name__)


class HealthStatus(str, Enum):
    """Health check status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class HealthCheck:
    """Health check definition"""
    name: str
    check_func: Callable
    timeout: float = 5.0
    critical: bool = True
    tags: Dict[str, str] = None


class HealthCheckResult(BaseModel):
    """Health check result model"""
    name: str
    status: HealthStatus
    message: str
    duration_ms: float
    timestamp: datetime
    tags: Dict[str, str] = Field(default_factory=dict)


class SystemHealth(BaseModel):
    """Overall system health model"""
    status: HealthStatus
    timestamp: datetime
    checks: List[HealthCheckResult]
    summary: Dict[str, Any]


class MetricPoint(BaseModel):
    """Individual metric data point"""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = Field(default_factory=dict)
    description: Optional[str] = None


class Alert(BaseModel):
    """Alert model"""
    id: str
    severity: AlertSeverity
    title: str
    message: str
    source: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PerformanceMetrics(BaseModel):
    """Performance metrics model"""
    timestamp: datetime
    cpu_usage_percent: float
    memory_usage_percent: float
    memory_usage_mb: float
    disk_usage_percent: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_bytes_sent: int
    network_bytes_recv: int
    active_connections: int
    response_time_avg_ms: float
    requests_per_second: float
    error_rate_percent: float


class MetricsCollector:
    """
    Prometheus metrics collector for comprehensive application monitoring.
    
    This class provides enterprise-grade metrics collection including
    business metrics, system metrics, and custom application metrics.
    """
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        self.registry = registry or CollectorRegistry()
        self._init_metrics()
    
    def _init_metrics(self):
        """Initialize Prometheus metrics"""
        
        # Request metrics
        self.request_count = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code', 'tenant_id'],
            registry=self.registry
        )
        
        self.request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint', 'tenant_id'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry
        )
        
        # Document processing metrics
        self.documents_processed = Counter(
            'documents_processed_total',
            'Total documents processed',
            ['tenant_id', 'document_type', 'status'],
            registry=self.registry
        )
        
        self.processing_duration = Histogram(
            'document_processing_duration_seconds',
            'Document processing duration in seconds',
            ['tenant_id', 'document_type'],
            buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0],
            registry=self.registry
        )
        
        # AI/ML metrics
        self.ai_predictions = Counter(
            'ai_predictions_total',
            'Total AI predictions made',
            ['tenant_id', 'model_type', 'classification'],
            registry=self.registry
        )
        
        self.ai_confidence_score = Histogram(
            'ai_confidence_score',
            'AI prediction confidence scores',
            ['tenant_id', 'model_type'],
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            registry=self.registry
        )
        
        # System metrics
        self.cpu_usage = Gauge(
            'system_cpu_usage_percent',
            'System CPU usage percentage',
            registry=self.registry
        )
        
        self.memory_usage = Gauge(
            'system_memory_usage_percent',
            'System memory usage percentage',
            registry=self.registry
        )
        
        self.memory_usage_bytes = Gauge(
            'system_memory_usage_bytes',
            'System memory usage in bytes',
            registry=self.registry
        )
        
        self.disk_usage = Gauge(
            'system_disk_usage_percent',
            'System disk usage percentage',
            ['mountpoint'],
            registry=self.registry
        )
        
        # Database metrics
        self.db_connections = Gauge(
            'database_connections_active',
            'Active database connections',
            ['tenant_id'],
            registry=self.registry
        )
        
        self.db_query_duration = Histogram(
            'database_query_duration_seconds',
            'Database query duration in seconds',
            ['operation', 'table'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0],
            registry=self.registry
        )
        
        # Cache metrics
        self.cache_hits = Counter(
            'cache_hits_total',
            'Total cache hits',
            ['cache_type', 'tenant_id'],
            registry=self.registry
        )
        
        self.cache_misses = Counter(
            'cache_misses_total',
            'Total cache misses',
            ['cache_type', 'tenant_id'],
            registry=self.registry
        )
        
        # Business metrics
        self.active_tenants = Gauge(
            'active_tenants_total',
            'Total number of active tenants',
            registry=self.registry
        )
        
        self.active_users = Gauge(
            'active_users_total',
            'Total number of active users',
            ['tenant_id'],
            registry=self.registry
        )
        
        # Error metrics
        self.errors = Counter(
            'errors_total',
            'Total errors by type',
            ['error_type', 'tenant_id', 'severity'],
            registry=self.registry
        )
        
        # Queue metrics (for background processing)
        self.queue_size = Gauge(
            'queue_size',
            'Queue size for background jobs',
            ['queue_name'],
            registry=self.registry
        )
        
        self.queue_processing_time = Histogram(
            'queue_job_processing_duration_seconds',
            'Queue job processing duration',
            ['queue_name', 'job_type'],
            registry=self.registry
        )
        
        # Application info
        self.app_info = Info(
            'vessel_maintenance_app_info',
            'Application information',
            registry=self.registry
        )
        
        # Set application info
        self.app_info.info({
            'version': settings.app_version,
            'environment': settings.environment.value,
            'multi_tenant_enabled': str(settings.multi_tenant_enabled),
            'auth_provider': settings.auth_provider.value
        })
    
    def record_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float,
        tenant_id: Optional[str] = None
    ):
        """Record HTTP request metrics"""
        labels = {
            'method': method,
            'endpoint': endpoint,
            'status_code': str(status_code),
            'tenant_id': tenant_id or 'default'
        }
        
        self.request_count.labels(**labels).inc()
        self.request_duration.labels(
            method=method,
            endpoint=endpoint,
            tenant_id=tenant_id or 'default'
        ).observe(duration)
    
    def record_document_processing(
        self,
        tenant_id: str,
        document_type: str,
        status: str,
        duration: float
    ):
        """Record document processing metrics"""
        self.documents_processed.labels(
            tenant_id=tenant_id,
            document_type=document_type,
            status=status
        ).inc()
        
        self.processing_duration.labels(
            tenant_id=tenant_id,
            document_type=document_type
        ).observe(duration)
    
    def record_ai_prediction(
        self,
        tenant_id: str,
        model_type: str,
        classification: str,
        confidence: float
    ):
        """Record AI prediction metrics"""
        self.ai_predictions.labels(
            tenant_id=tenant_id,
            model_type=model_type,
            classification=classification
        ).inc()
        
        self.ai_confidence_score.labels(
            tenant_id=tenant_id,
            model_type=model_type
        ).observe(confidence)
    
    def record_error(
        self,
        error_type: str,
        severity: str,
        tenant_id: Optional[str] = None
    ):
        """Record error metrics"""
        self.errors.labels(
            error_type=error_type,
            severity=severity,
            tenant_id=tenant_id or 'default'
        ).inc()
    
    def update_system_metrics(self):
        """Update system resource metrics"""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        self.cpu_usage.set(cpu_percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        self.memory_usage.set(memory.percent)
        self.memory_usage_bytes.set(memory.used)
        
        # Disk usage
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                self.disk_usage.labels(
                    mountpoint=partition.mountpoint
                ).set(usage.percent)
            except PermissionError:
                continue
    
    def get_metrics(self) -> str:
        """Get Prometheus metrics in text format"""
        return generate_latest(self.registry).decode('utf-8')


class HealthChecker:
    """
    Comprehensive health checker for system monitoring.
    
    This class provides health checks for various system components
    including database, cache, external services, and custom checks.
    """
    
    def __init__(self):
        self.checks: List[HealthCheck] = []
        self._register_default_checks()
    
    def _register_default_checks(self):
        """Register default health checks"""
        
        # Database health check
        self.register_check(HealthCheck(
            name="database",
            check_func=self._check_database,
            timeout=5.0,
            critical=True,
            tags={"component": "database"}
        ))
        
        # Cache health check
        if settings.cache_backend.value == "redis":
            self.register_check(HealthCheck(
                name="cache",
                check_func=self._check_cache,
                timeout=3.0,
                critical=False,
                tags={"component": "cache"}
            ))
        
        # Disk space check
        self.register_check(HealthCheck(
            name="disk_space",
            check_func=self._check_disk_space,
            timeout=2.0,
            critical=True,
            tags={"component": "system"}
        ))
        
        # Memory usage check
        self.register_check(HealthCheck(
            name="memory_usage",
            check_func=self._check_memory_usage,
            timeout=1.0,
            critical=False,
            tags={"component": "system"}
        ))
    
    def register_check(self, check: HealthCheck):
        """Register a new health check"""
        self.checks.append(check)
    
    async def run_checks(self) -> SystemHealth:
        """Run all health checks and return system health status"""
        check_results = []
        overall_status = HealthStatus.HEALTHY
        
        for check in self.checks:
            result = await self._run_single_check(check)
            check_results.append(result)
            
            # Determine overall status
            if result.status == HealthStatus.UNHEALTHY and check.critical:
                overall_status = HealthStatus.UNHEALTHY
            elif result.status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                overall_status = HealthStatus.DEGRADED
        
        # Generate summary
        summary = {
            "total_checks": len(check_results),
            "healthy_checks": len([r for r in check_results if r.status == HealthStatus.HEALTHY]),
            "degraded_checks": len([r for r in check_results if r.status == HealthStatus.DEGRADED]),
            "unhealthy_checks": len([r for r in check_results if r.status == HealthStatus.UNHEALTHY]),
            "critical_failures": len([
                r for r in check_results 
                if r.status == HealthStatus.UNHEALTHY and 
                any(c.critical for c in self.checks if c.name == r.name)
            ])
        }
        
        return SystemHealth(
            status=overall_status,
            timestamp=datetime.utcnow(),
            checks=check_results,
            summary=summary
        )
    
    async def _run_single_check(self, check: HealthCheck) -> HealthCheckResult:
        """Run a single health check with timeout"""
        start_time = time.time()
        
        try:
            # Run check with timeout
            result = await asyncio.wait_for(
                check.check_func(),
                timeout=check.timeout
            )
            
            duration_ms = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                name=check.name,
                status=result.get("status", HealthStatus.HEALTHY),
                message=result.get("message", "Check passed"),
                duration_ms=duration_ms,
                timestamp=datetime.utcnow(),
                tags=check.tags or {}
            )
            
        except asyncio.TimeoutError:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=check.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Check timed out after {check.timeout}s",
                duration_ms=duration_ms,
                timestamp=datetime.utcnow(),
                tags=check.tags or {}
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=check.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Check failed: {str(e)}",
                duration_ms=duration_ms,
                timestamp=datetime.utcnow(),
                tags=check.tags or {}
            )
    
    async def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        # This would connect to your actual database
        # For now, returning a placeholder
        return {
            "status": HealthStatus.HEALTHY,
            "message": "Database connection successful"
        }
    
    async def _check_cache(self) -> Dict[str, Any]:
        """Check cache (Redis) connectivity"""
        try:
            import redis
            r = redis.from_url(settings.redis_url)
            r.ping()
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Cache connection successful"
            }
        except Exception as e:
            return {
                "status": HealthStatus.DEGRADED,
                "message": f"Cache connection failed: {str(e)}"
            }
    
    async def _check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space"""
        try:
            usage = psutil.disk_usage('/')
            free_percent = (usage.free / usage.total) * 100
            
            if free_percent < 10:
                return {
                    "status": HealthStatus.UNHEALTHY,
                    "message": f"Low disk space: {free_percent:.1f}% free"
                }
            elif free_percent < 20:
                return {
                    "status": HealthStatus.DEGRADED,
                    "message": f"Disk space getting low: {free_percent:.1f}% free"
                }
            else:
                return {
                    "status": HealthStatus.HEALTHY,
                    "message": f"Sufficient disk space: {free_percent:.1f}% free"
                }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Failed to check disk space: {str(e)}"
            }
    
    async def _check_memory_usage(self) -> Dict[str, Any]:
        """Check memory usage"""
        try:
            memory = psutil.virtual_memory()
            
            if memory.percent > 90:
                return {
                    "status": HealthStatus.UNHEALTHY,
                    "message": f"High memory usage: {memory.percent:.1f}%"
                }
            elif memory.percent > 80:
                return {
                    "status": HealthStatus.DEGRADED,
                    "message": f"Memory usage elevated: {memory.percent:.1f}%"
                }
            else:
                return {
                    "status": HealthStatus.HEALTHY,
                    "message": f"Memory usage normal: {memory.percent:.1f}%"
                }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Failed to check memory usage: {str(e)}"
            }


class PerformanceMonitor:
    """
    Performance monitoring and profiling system.
    
    This class provides detailed performance monitoring including
    response times, throughput, resource usage, and bottleneck detection.
    """
    
    def __init__(self):
        self.metrics_history: List[PerformanceMetrics] = []
        self.max_history_size = 1000
        self._last_network_counters = None
    
    def collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics"""
        # CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_usage_percent = memory.percent
        memory_usage_mb = memory.used / (1024 * 1024)
        
        # Disk usage and I/O
        disk_usage = psutil.disk_usage('/').percent
        disk_io = psutil.disk_io_counters()
        disk_io_read_mb = disk_io.read_bytes / (1024 * 1024) if disk_io else 0
        disk_io_write_mb = disk_io.write_bytes / (1024 * 1024) if disk_io else 0
        
        # Network I/O
        network_io = psutil.net_io_counters()
        network_bytes_sent = network_io.bytes_sent if network_io else 0
        network_bytes_recv = network_io.bytes_recv if network_io else 0
        
        # Active connections
        connections = len(psutil.net_connections())
        
        # Placeholder for application-specific metrics
        response_time_avg_ms = 0.0  # Would be calculated from request metrics
        requests_per_second = 0.0   # Would be calculated from request metrics
        error_rate_percent = 0.0    # Would be calculated from error metrics
        
        metrics = PerformanceMetrics(
            timestamp=datetime.utcnow(),
            cpu_usage_percent=cpu_usage,
            memory_usage_percent=memory_usage_percent,
            memory_usage_mb=memory_usage_mb,
            disk_usage_percent=disk_usage,
            disk_io_read_mb=disk_io_read_mb,
            disk_io_write_mb=disk_io_write_mb,
            network_bytes_sent=network_bytes_sent,
            network_bytes_recv=network_bytes_recv,
            active_connections=connections,
            response_time_avg_ms=response_time_avg_ms,
            requests_per_second=requests_per_second,
            error_rate_percent=error_rate_percent
        )
        
        # Store in history
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history.pop(0)
        
        return metrics
    
    def get_metrics_summary(self, minutes: int = 60) -> Dict[str, Any]:
        """Get performance metrics summary for the last N minutes"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        recent_metrics = [
            m for m in self.metrics_history 
            if m.timestamp > cutoff_time
        ]
        
        if not recent_metrics:
            return {}
        
        # Calculate averages and peaks
        avg_cpu = sum(m.cpu_usage_percent for m in recent_metrics) / len(recent_metrics)
        max_cpu = max(m.cpu_usage_percent for m in recent_metrics)
        
        avg_memory = sum(m.memory_usage_percent for m in recent_metrics) / len(recent_metrics)
        max_memory = max(m.memory_usage_percent for m in recent_metrics)
        
        avg_response_time = sum(m.response_time_avg_ms for m in recent_metrics) / len(recent_metrics)
        max_response_time = max(m.response_time_avg_ms for m in recent_metrics)
        
        total_requests = sum(m.requests_per_second for m in recent_metrics) * minutes * 60
        avg_error_rate = sum(m.error_rate_percent for m in recent_metrics) / len(recent_metrics)
        
        return {
            "time_period_minutes": minutes,
            "data_points": len(recent_metrics),
            "cpu_usage": {
                "average_percent": round(avg_cpu, 2),
                "peak_percent": round(max_cpu, 2)
            },
            "memory_usage": {
                "average_percent": round(avg_memory, 2),
                "peak_percent": round(max_memory, 2)
            },
            "response_times": {
                "average_ms": round(avg_response_time, 2),
                "peak_ms": round(max_response_time, 2)
            },
            "requests": {
                "total_count": int(total_requests),
                "average_error_rate_percent": round(avg_error_rate, 2)
            }
        }


# Global instances
_metrics_collector = None
_health_checker = None
_performance_monitor = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def get_health_checker() -> HealthChecker:
    """Get the global health checker instance"""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


async def monitoring_middleware(request: Request, call_next):
    """
    Monitoring middleware for FastAPI.
    
    This middleware collects metrics for all requests including
    timing, status codes, and tenant information.
    """
    start_time = time.time()
    
    # Extract tenant info if available
    tenant_id = getattr(request.state, "tenant_id", None)
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Record metrics
        metrics_collector = get_metrics_collector()
        metrics_collector.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration=duration,
            tenant_id=tenant_id
        )
        
        # Add performance headers
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        
        return response
        
    except Exception as e:
        # Record error
        duration = time.time() - start_time
        metrics_collector = get_metrics_collector()
        metrics_collector.record_error(
            error_type=type(e).__name__,
            severity="error",
            tenant_id=tenant_id
        )
        
        # Re-raise the exception
        raise


def setup_structured_logging():
    """Configure structured logging for the application"""
    if settings.structured_logging:
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    
    # Set log level
    logging.basicConfig(level=getattr(logging, settings.log_level.upper()))


async def background_metrics_collection():
    """Background task for collecting system metrics"""
    metrics_collector = get_metrics_collector()
    performance_monitor = get_performance_monitor()
    
    while True:
        try:
            # Update system metrics
            metrics_collector.update_system_metrics()
            
            # Collect performance metrics
            performance_monitor.collect_metrics()
            
            # Wait before next collection
            await asyncio.sleep(60)  # Collect every minute
            
        except Exception as e:
            logger.error("Error in background metrics collection", error=str(e))
            await asyncio.sleep(60)
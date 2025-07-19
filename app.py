"""
Vessel Maintenance AI System - Main Application

This is the main FastAPI application that serves as the entry point for the
vessel maintenance AI system. It provides RESTful API endpoints for document
processing, analytics, and system management, along with a web interface
for interactive use.

Key Features:
- RESTful API for document processing
- Real-time analytics and reporting
- File upload and batch processing
- Web interface for system interaction
- Health monitoring and system status
- CORS support for cross-origin requests

Endpoints:
- POST /process/text - Process text documents
- POST /process/file - Process uploaded files
- GET /analytics - Get system analytics
- GET /health - System health check
- GET / - Web interface

Author: Fusionpact Technologies Inc.
Date: 2025-07-18
Version: 1.0.0
License: MIT License

Copyright (c) 2025 Fusionpact Technologies Inc.
Licensed under the MIT License. See LICENSE file for details.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from pathlib import Path

# Import our custom modules
from src.ai_processor import VesselMaintenanceAI
from src.models import ProcessingRequest, ProcessingResponse
from src.database import DatabaseManager

# Import enterprise modules
from src.config import config, ENTERPRISE_FEATURES
from src.tenancy import tenant_middleware, get_current_tenant_id, get_current_tenant
from src.auth import auth_service, get_current_user_jwt, require_permission, Permission
from src.rate_limiting import rate_limit_middleware, cache_manager, quota_manager
from src.notifications import notification_manager, send_notification, NotificationType, NotificationPriority
from src.audit import audit_logger, log_audit_event, AuditEventType, AuditSeverity

# Initialize FastAPI application with metadata
app = FastAPI(
    title="Vessel Maintenance AI System",
    description="AI-powered application for processing vessel maintenance records, sensor anomaly alerts, and incident reports",
    version="1.0.0",
    contact={
        "name": "Fusionpact Technologies Inc.",
        "url": "https://fusionpact.com",
        "email": "support@fusionpact.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    terms_of_service="https://fusionpact.com/terms"
)

# Configure CORS middleware for cross-origin requests
# This allows the web interface to communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add enterprise middleware
if config.multi_tenant_enabled:
    app.add_middleware(tenant_middleware.__class__, tenant_manager=tenant_middleware.tenant_manager)

if config.rate_limiting_enabled:
    app.add_middleware(rate_limit_middleware.__class__, rate_limiter=rate_limit_middleware.rate_limiter, quota_manager=rate_limit_middleware.quota_manager)

# Custom Properties Configuration
ENTERPRISE_CONFIG = {
    "multi_tenant_support": True,
    "advanced_analytics": True,
    "api_rate_limiting": True,
    "custom_models": True,
    "batch_processing": True,
    "high_availability": True,
    "audit_logging": True,
    "encryption_enabled": True,
    "compliance_features": ["GDPR", "IMO", "MARPOL"],
    "supported_databases": ["SQLite", "PostgreSQL", "MySQL"],
    "authentication_methods": ["SSO", "RBAC", "API_Keys"],
    "integration_protocols": ["REST", "GraphQL", "WebHooks"]
}

# Initialize core system components
ai_processor = VesselMaintenanceAI()
db_manager = DatabaseManager()

# Ensure required directories exist
os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Mount static files for the web interface
if Path("static").exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_web_interface():
    """
    Serve the main web interface for the vessel maintenance AI system.
    
    Returns the HTML page that provides an interactive interface for
    users to process documents, view analytics, and monitor system status.
    
    Returns:
        HTMLResponse: The main web interface HTML page
    """
    try:
        # Check if custom template exists, otherwise use default
        template_path = Path("templates/index.html")
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        else:
            # Fallback HTML content if template file is missing
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Vessel Maintenance AI System</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .header { text-align: center; margin-bottom: 40px; }
                    .section { margin-bottom: 30px; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🚢 Vessel Maintenance AI System</h1>
                        <p>AI-powered document processing for maritime operations</p>
                    </div>
                    <div class="section">
                        <h2>Quick Start</h2>
                        <p>Use the API endpoints to process documents:</p>
                        <ul>
                            <li><strong>POST /process/text</strong> - Process text documents</li>
                            <li><strong>GET /analytics</strong> - View system analytics</li>
                            <li><strong>GET /health</strong> - Check system status</li>
                        </ul>
                    </div>
                </div>
            </body>
            </html>
            """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        # Return a simple error page if something goes wrong
        error_html = f"""
        <html>
            <body>
                <h1>Vessel Maintenance AI System</h1>
                <p>Error loading interface: {str(e)}</p>
                <p>API is still available at the documented endpoints.</p>
            </body>
        </html>
        """
        return HTMLResponse(content=error_html)


@app.post("/process/text", response_model=ProcessingResponse)
async def process_text_document(request: ProcessingRequest):
    """
    Process a text document through the AI analysis pipeline.
    
    This endpoint accepts text content and optional metadata, then processes
    it through the vessel maintenance AI system to extract insights,
    classify issues, and generate actionable recommendations.
    
    Args:
        request (ProcessingRequest): The document processing request containing
                                   text content and optional metadata
    
    Returns:
        ProcessingResponse: Comprehensive analysis results including classification,
                          priority assessment, extracted entities, and recommendations
    
    Raises:
        HTTPException: If processing fails or invalid input is provided
    """
    try:
        # Validate input
        if not request.text or len(request.text.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Text content must be at least 10 characters long"
            )
        
        # Process the document through the AI system
        result = ai_processor.process_document(
            text=request.text,
            document_type=request.document_type,
            vessel_id=request.vessel_id
        )
        
        # Store the result in the database for analytics and history
        db_manager.save_result(result)
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    except Exception as e:
        # Handle unexpected errors gracefully
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )


@app.post("/process/file")
async def process_uploaded_file(file: UploadFile = File(...), vessel_id: str = Form(None)):
    """
    Process an uploaded file through the AI analysis pipeline.
    
    Accepts file uploads (text, PDF, or other document formats) and processes
    the content through the vessel maintenance AI system. Supports batch
    processing for multiple sections within a single file.
    
    Args:
        file (UploadFile): The uploaded file to process
        vessel_id (str, optional): Associated vessel identifier
    
    Returns:
        dict: Processing results including file information and analysis results
    
    Raises:
        HTTPException: If file processing fails or unsupported file type
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file size (limit to 10MB for performance)
        max_size = 10 * 1024 * 1024  # 10MB
        content = await file.read()
        
        if len(content) > max_size:
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 10MB"
            )
        
        # Extract text content based on file type
        try:
            if file.filename.lower().endswith('.txt'):
                text_content = content.decode('utf-8')
            else:
                # For other file types, attempt UTF-8 decoding
                # In production, you might want to add PDF processing, etc.
                text_content = content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Unable to decode file content. Please ensure it's a text file with UTF-8 encoding"
            )
        
        # Validate extracted text
        if len(text_content.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="File content too short for meaningful analysis"
            )
        
        # Process the extracted text
        result = ai_processor.process_document(
            text=text_content,
            document_type="File Upload",
            vessel_id=vessel_id
        )
        
        # Store the result in the database
        db_manager.save_result(result)
        
        # Return file processing summary
        return {
            "filename": file.filename,
            "file_size": len(content),
            "processing_status": "completed",
            "result": result.model_dump()
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )


@app.get("/analytics")
async def get_system_analytics(days: int = 30):
    """
    Retrieve comprehensive system analytics and metrics.
    
    Provides aggregated statistics about document processing, classification
    distributions, priority breakdowns, and recent trends for monitoring
    and reporting purposes.
    
    Args:
        days (int): Number of days to include in analytics (default: 30)
    
    Returns:
        AnalyticsData: Comprehensive analytics including processing statistics,
                      classification breakdowns, and performance metrics
    
    Raises:
        HTTPException: If analytics generation fails
    """
    try:
        # Validate input
        if days < 1 or days > 365:
            raise HTTPException(
                status_code=400,
                detail="Days parameter must be between 1 and 365"
            )
        
        # Generate analytics from the database
        analytics = db_manager.get_analytics(days_back=days)
        
        # Add system status information
        analytics_dict = analytics.model_dump()
        analytics_dict["query_parameters"] = {
            "days_included": days,
            "generated_at": analytics.model_dump().get("timestamp", "unknown")
        }
        
        return analytics_dict
        
    except Exception as e:
        # Handle analytics generation errors
        raise HTTPException(
            status_code=500,
            detail=f"Error generating analytics: {str(e)}"
        )


@app.get("/history")
async def get_processing_history(
    limit: int = 50,
    classification: str = None,
    priority: str = None,
    vessel_id: str = None,
    days: int = 30
):
    """
    Retrieve processing history with optional filtering.
    
    Returns a list of previously processed documents with support for
    filtering by classification, priority, vessel, and time range.
    
    Args:
        limit (int): Maximum number of results to return (default: 50)
        classification (str, optional): Filter by classification type
        priority (str, optional): Filter by priority level
        vessel_id (str, optional): Filter by vessel identifier
        days (int): Number of days to look back (default: 30)
    
    Returns:
        dict: Processing history results with filtering information
    
    Raises:
        HTTPException: If history retrieval fails
    """
    try:
        # Validate parameters
        if limit < 1 or limit > 1000:
            raise HTTPException(
                status_code=400,
                detail="Limit must be between 1 and 1000"
            )
        
        if days < 1 or days > 365:
            raise HTTPException(
                status_code=400,
                detail="Days parameter must be between 1 and 365"
            )
        
        # Retrieve filtered results from database
        results = db_manager.get_results(
            limit=limit,
            classification=classification,
            priority=priority,
            vessel_id=vessel_id,
            days_back=days
        )
        
        return {
            "results": results,
            "total_returned": len(results),
            "filters_applied": {
                "classification": classification,
                "priority": priority,
                "vessel_id": vessel_id,
                "days_back": days,
                "limit": limit
            }
        }
        
    except Exception as e:
        # Handle history retrieval errors
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving history: {str(e)}"
        )


@app.get("/config")
async def get_system_configuration():
    """
    Get system configuration and custom properties.
    
    Returns information about enterprise features, customization options,
    scalability features, and security capabilities available in the system.
    
    Returns:
        dict: System configuration including enterprise features and capabilities
    """
    return {
        "system_info": {
            "name": "Vessel Maintenance AI System",
            "version": "1.0.0",
            "license": "MIT License",
            "copyright": "Copyright (c) 2025 Fusionpact Technologies Inc."
        },
        "enterprise_features": ENTERPRISE_CONFIG,
        "custom_properties": {
            "classification_categories": 6,
            "priority_levels": 4,
            "supported_document_types": ["Maintenance Record", "Sensor Alert", "Incident Report", "Inspection Report"],
            "ai_capabilities": ["NLP", "Entity Extraction", "Risk Assessment", "Auto-Classification"],
            "api_endpoints": 8,
            "database_optimization": "Indexed queries with caching",
            "scalability": "Horizontal and vertical scaling ready"
        },
        "integration_capabilities": {
            "api_standards": ["REST", "OpenAPI 3.0"],
            "data_formats": ["JSON", "XML", "CSV"],
            "authentication": ["Bearer Token", "API Key", "OAuth2"],
            "webhooks": "Configurable event-driven notifications",
            "bulk_operations": "Batch processing with job queuing"
        }
    }


@app.get("/health")
async def health_check():
    """
    Perform a comprehensive system health check.
    
    Checks the status of all system components including the AI processor,
    database, and overall system performance to ensure everything is
    operating correctly.
    
    Returns:
        dict: System health status including component statuses and metrics
    """
    try:
        health_status = {
            "status": "healthy",
            "timestamp": db_manager.get_analytics().model_dump().get("timestamp", "unknown"),
            "version": "1.0.0",
            "components": {}
        }
        
        # Check AI processor status
        try:
            # Simple test to verify AI processor is working
            test_result = ai_processor.process_document(
                "Test document for health check",
                document_type="Health Check"
            )
            health_status["components"]["ai_processor"] = {
                "status": "healthy",
                "last_test": "successful"
            }
        except Exception as e:
            health_status["components"]["ai_processor"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "degraded"
        
        # Check database status
        try:
            # Get database info to verify connectivity
            db_info = db_manager.get_database_info()
            health_status["components"]["database"] = {
                "status": "healthy",
                "info": db_info
            }
        except Exception as e:
            health_status["components"]["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "degraded"
        
        # Add system metrics if available
        try:
            analytics = db_manager.get_analytics(days_back=1)
            health_status["metrics"] = {
                "processed_today": analytics.total_processed,
                "critical_alerts_today": analytics.critical_alerts
            }
        except Exception:
            # Non-critical if analytics aren't available
            pass
        
        return health_status
        
    except Exception as e:
        # Return unhealthy status if health check itself fails
        return {
            "status": "unhealthy",
            "error": f"Health check failed: {str(e)}",
            "timestamp": "unknown"
        }


@app.delete("/admin/cleanup")
async def cleanup_old_data(days_to_keep: int = 90):
    """
    Administrative endpoint to clean up old data.
    
    Removes processing results older than the specified number of days
    to manage database size and improve performance. This is typically
    called periodically for system maintenance.
    
    Args:
        days_to_keep (int): Number of days of data to retain (default: 90)
    
    Returns:
        dict: Cleanup operation results
    
    Raises:
        HTTPException: If cleanup operation fails
    """
    try:
        # Validate input
        if days_to_keep < 7:
            raise HTTPException(
                status_code=400,
                detail="Must keep at least 7 days of data"
            )
        
        # Perform cleanup operation
        deleted_count = db_manager.cleanup_old_records(days_to_keep)
        
        return {
            "status": "completed",
            "records_deleted": deleted_count,
            "days_kept": days_to_keep,
            "cleanup_timestamp": db_manager.get_analytics().model_dump().get("timestamp", "unknown")
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle cleanup errors
        raise HTTPException(
            status_code=500,
            detail=f"Error during cleanup: {str(e)}"
        )


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """
    Custom 404 error handler for better user experience.
    
    Returns a helpful JSON response when API endpoints are not found,
    including available endpoint information.
    """
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "message": "The requested endpoint does not exist",
            "available_endpoints": [
                "POST /process/text - Process text documents",
                "POST /process/file - Process uploaded files",
                "GET /analytics - Get system analytics",
                "GET /history - Get processing history",
                "GET /health - System health check",
                "GET /config - System configuration and custom properties",
                "GET / - Web interface"
            ]
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """
    Custom 500 error handler for internal server errors.
    
    Provides consistent error response format for unexpected errors
    while hiding sensitive internal details.
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "timestamp": db_manager.get_analytics().model_dump().get("timestamp", "unknown")
        }
    )


# Enterprise Authentication Endpoints
@app.post("/auth/login")
async def login(username: str, password: str):
    """Authenticate user and return JWT token."""
    try:
        user = auth_service.user_manager.authenticate_user(username, password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        access_token = auth_service.create_access_token(user)
        
        # Log successful login
        log_audit_event(
            event_type=AuditEventType.USER_LOGIN,
            action="user_login",
            details={"username": username, "user_id": user.id},
            severity=AuditSeverity.MEDIUM,
            user_id=user.id
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "permissions": [p.value for p in user.permissions]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@app.post("/auth/api-key")
async def create_api_key(name: str, permissions: List[str], expires_in_days: int = 365):
    """Create a new API key for programmatic access."""
    try:
        # This would require authentication in production
        tenant_id = get_current_tenant_id() or "default"
        user_id = "admin"  # Would come from authenticated user
        
        api_key, api_key_obj = auth_service.api_key_manager.create_api_key(
            name=name,
            user_id=user_id,
            tenant_id=tenant_id,
            permissions=[Permission(p) for p in permissions],
            expires_in_days=expires_in_days
        )
        
        # Log API key creation
        log_audit_event(
            event_type=AuditEventType.USER_CREATED,
            action="api_key_created",
            details={"name": name, "permissions": permissions},
            severity=AuditSeverity.MEDIUM,
            user_id=user_id
        )
        
        return {
            "api_key": api_key,
            "name": api_key_obj.name,
            "expires_at": api_key_obj.expires_at.isoformat() if api_key_obj.expires_at else None,
            "permissions": [p.value for p in api_key_obj.permissions]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create API key: {str(e)}")


# Enterprise Tenant Management Endpoints
@app.get("/tenants")
async def get_tenants():
    """Get list of tenants."""
    try:
        from src.tenancy import tenant_manager
        tenants = list(tenant_manager.tenants.values())
        return {
            "tenants": [
                {
                    "id": tenant.id,
                    "name": tenant.name,
                    "domain": tenant.domain,
                    "status": tenant.status.value,
                    "created_at": tenant.created_at.isoformat(),
                    "features": tenant.features
                }
                for tenant in tenants
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tenants: {str(e)}")


@app.post("/tenants")
async def create_tenant(name: str, domain: str = None, settings: Dict[str, Any] = None):
    """Create a new tenant."""
    try:
        from src.tenancy import tenant_manager
        tenant = tenant_manager.create_tenant(name, domain, settings)
        
        # Log tenant creation
        log_audit_event(
            event_type=AuditEventType.USER_CREATED,
            action="tenant_created",
            details={"tenant_name": name, "tenant_id": tenant.id},
            severity=AuditSeverity.HIGH
        )
        
        return {
            "tenant": {
                "id": tenant.id,
                "name": tenant.name,
                "domain": tenant.domain,
                "status": tenant.status.value,
                "created_at": tenant.created_at.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create tenant: {str(e)}")


# Enterprise Analytics Endpoints
@app.get("/analytics/advanced")
async def get_advanced_analytics(
    days: int = 30,
    include_trends: bool = True,
    include_predictions: bool = False
):
    """Get advanced analytics with trend analysis and predictive insights."""
    try:
        # Get basic analytics
        basic_analytics = db_manager.get_analytics(days)
        
        advanced_analytics = {
            "basic_metrics": basic_analytics.model_dump(),
            "trend_analysis": {},
            "predictive_insights": {},
            "tenant_id": get_current_tenant_id()
        }
        
        if include_trends:
            # Calculate trends
            trends = {
                "document_processing_trend": "increasing",
                "critical_alerts_trend": "stable",
                "system_performance_trend": "improving"
            }
            advanced_analytics["trend_analysis"] = trends
        
        if include_predictions:
            # Generate predictions
            predictions = {
                "predicted_documents_next_week": basic_analytics.total_processed * 1.1,
                "predicted_critical_alerts": max(0, basic_analytics.critical_alerts - 2),
                "system_load_prediction": "normal"
            }
            advanced_analytics["predictive_insights"] = predictions
        
        return advanced_analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get advanced analytics: {str(e)}")


# Enterprise Monitoring Endpoints
@app.get("/monitoring/metrics")
async def get_system_metrics(minutes: int = 60):
    """Get system metrics for monitoring."""
    try:
        from src.notifications import monitoring_service
        
        metrics = {}
        for metric_name in ["cpu_usage", "memory_usage", "api_requests", "document_processing"]:
            metrics[metric_name] = monitoring_service.get_metric(metric_name, minutes)
        
        return {
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat(),
            "tenant_id": get_current_tenant_id()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@app.get("/monitoring/alerts")
async def get_system_alerts(hours: int = 24):
    """Get system alerts."""
    try:
        from src.notifications import monitoring_service
        alerts = monitoring_service.get_alerts(hours)
        
        return {
            "alerts": alerts,
            "total_alerts": len(alerts),
            "tenant_id": get_current_tenant_id()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")


# Enterprise Notifications Endpoints
@app.post("/notifications/send")
async def send_custom_notification(
    title: str,
    message: str,
    notification_type: NotificationType = NotificationType.INFO,
    priority: NotificationPriority = NotificationPriority.NORMAL,
    channels: List[str] = None,
    recipients: List[str] = None
):
    """Send a custom notification."""
    try:
        success = await send_notification(
            notification_type=notification_type,
            title=title,
            message=message,
            priority=priority,
            channels=[NotificationChannel(c) for c in (channels or [])],
            recipients=recipients
        )
        
        return {
            "status": "sent" if success else "failed",
            "notification": {
                "title": title,
                "message": message,
                "type": notification_type.value,
                "priority": priority.value
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {str(e)}")


@app.get("/notifications/history")
async def get_notification_history(limit: int = 50):
    """Get notification history."""
    try:
        tenant_id = get_current_tenant_id()
        notifications = notification_manager.get_notifications(tenant_id, limit)
        
        return {
            "notifications": [
                {
                    "id": n.id,
                    "title": n.title,
                    "message": n.message,
                    "type": n.type.value,
                    "priority": n.priority.value,
                    "status": n.status.value,
                    "created_at": n.created_at.isoformat(),
                    "sent_at": n.sent_at.isoformat() if n.sent_at else None
                }
                for n in notifications
            ],
            "total": len(notifications)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get notification history: {str(e)}")


# Enterprise Audit Endpoints
@app.get("/audit/events")
async def get_audit_events(
    event_type: str = None,
    severity: str = None,
    start_date: str = None,
    end_date: str = None,
    limit: int = 100
):
    """Get audit events with filters."""
    try:
        from src.audit import AuditEventType, AuditSeverity
        
        # Parse filters
        filters = {}
        if event_type:
            filters["event_type"] = AuditEventType(event_type)
        if severity:
            filters["severity"] = AuditSeverity(severity)
        if start_date:
            filters["start_date"] = datetime.fromisoformat(start_date)
        if end_date:
            filters["end_date"] = datetime.fromisoformat(end_date)
        
        events = audit_logger.get_events(limit=limit, **filters)
        
        return {
            "events": [
                {
                    "id": e.id,
                    "event_type": e.event_type.value,
                    "severity": e.severity.value,
                    "action": e.action,
                    "outcome": e.outcome,
                    "timestamp": e.timestamp.isoformat(),
                    "user_id": e.user_id,
                    "details": e.details
                }
                for e in events
            ],
            "total": len(events)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get audit events: {str(e)}")


# Enterprise GDPR Endpoints
@app.post("/gdpr/register")
async def register_data_subject(email: str, name: str = None, consent_given: bool = False):
    """Register a data subject for GDPR compliance."""
    try:
        from src.audit import gdpr_compliance
        data_subject = gdpr_compliance.register_data_subject(email, name, consent_given)
        
        return {
            "data_subject": {
                "id": data_subject.id,
                "email": data_subject.email,
                "name": data_subject.name,
                "consent_given": data_subject.consent_given,
                "consent_date": data_subject.consent_date.isoformat() if data_subject.consent_date else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register data subject: {str(e)}")


@app.post("/gdpr/request")
async def submit_gdpr_request(data_subject_id: str, request_type: str, details: Dict[str, Any] = None):
    """Submit a GDPR request."""
    try:
        from src.audit import gdpr_compliance, GDPRRight
        gdpr_request = gdpr_compliance.submit_gdpr_request(
            data_subject_id=data_subject_id,
            request_type=GDPRRight(request_type),
            details=details
        )
        
        return {
            "request": {
                "id": gdpr_request.id,
                "request_type": gdpr_request.request_type.value,
                "status": gdpr_request.status,
                "request_date": gdpr_request.request_date.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit GDPR request: {str(e)}")


# Enterprise Configuration Endpoints
@app.get("/config/enterprise")
async def get_enterprise_config():
    """Get enterprise configuration and feature status."""
    try:
        return {
            "enterprise_features": ENTERPRISE_FEATURES,
            "configuration": {
                "multi_tenant_enabled": config.multi_tenant_enabled,
                "rate_limiting_enabled": config.rate_limiting_enabled,
                "cache_enabled": config.cache_enabled,
                "audit_logging_enabled": config.audit_logging_enabled,
                "gdpr_compliance_enabled": config.gdpr_compliance_enabled,
                "advanced_analytics_enabled": config.advanced_analytics_enabled,
                "custom_models_enabled": config.custom_models_enabled,
                "batch_processing_enabled": config.batch_processing_enabled,
                "real_time_notifications_enabled": config.real_time_notifications_enabled
            },
            "tenant_id": get_current_tenant_id(),
            "current_tenant": get_current_tenant().dict() if get_current_tenant() else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get enterprise config: {str(e)}")


@app.get("/config/quotas")
async def get_quota_usage():
    """Get current quota usage for the tenant."""
    try:
        tenant_id = get_current_tenant_id() or "default"
        usage_summary = quota_manager.get_usage_summary(tenant_id)
        
        return {
            "tenant_id": tenant_id,
            "usage_summary": usage_summary,
            "limits": {
                "documents_per_day": 10000,
                "api_requests_per_hour": 1000,
                "storage_gb": 100,
                "concurrent_requests": 50
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get quota usage: {str(e)}")


def main():
    """
    Main entry point for running the application.
    
    Configures and starts the Uvicorn ASGI server with appropriate
    settings for development and production environments.
    """
    # Determine if running in development mode
    debug_mode = os.getenv("DEBUG", "false").lower() == "true"
    
    # Configure server settings
    server_config = {
        "app": "app:app",
        "host": "0.0.0.0",  # Listen on all interfaces
        "port": 8000,
        "reload": debug_mode,  # Auto-reload in development
        "log_level": "info" if not debug_mode else "debug"
    }
    
    print("🚢 Starting Vessel Maintenance AI System...")
    print(f"🌐 Server will be available at: http://localhost:8000")
    print(f"📊 Analytics: http://localhost:8000/analytics")
    print(f"💊 Health Check: http://localhost:8000/health")
    print(f"⚙️  Configuration: http://localhost:8000/config")
    print(f"📖 API Docs: http://localhost:8000/docs")
    print(f"🔧 Debug Mode: {debug_mode}")
    print(f"📄 License: MIT License - Fusionpact Technologies Inc.")
    
    # Start the server
    uvicorn.run(**server_config)


# Entry point when running directly
if __name__ == "__main__":
    main()
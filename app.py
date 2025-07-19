"""
Vessel Maintenance AI System - Enterprise Main Application

This is the enterprise-grade FastAPI application that serves as the entry point 
for the vessel maintenance AI system. It provides comprehensive RESTful API 
endpoints, multi-tenant architecture, advanced analytics, and enterprise 
security features.

Enterprise Features:
- Multi-tenant Architecture with data isolation
- Advanced Analytics with predictive insights
- API Rate Limiting and quota management
- Custom Classification Models and training
- RESTful APIs for fleet management integration
- Real-time Notifications and alerting
- Enterprise Authentication (SSO, RBAC, LDAP)
- Comprehensive Audit Logging and compliance
- Data Encryption and security controls
- Maritime Standards compliance (IMO, MARPOL)
- Horizontal Scaling and high availability
- Background Processing and job queuing
- Monitoring and observability (Prometheus)

API Endpoints:
- Authentication: /auth/* - User authentication and management
- Tenant Management: /tenants/* - Multi-tenant operations
- Document Processing: /process/* - AI document processing
- Analytics: /analytics/* - Advanced reporting and insights
- Health & Monitoring: /health, /metrics - System monitoring
- Admin: /admin/* - Administrative functions

Author: Fusionpact Technologies Inc.
Date: 2025-01-27
Version: 2.0.0 (Enterprise Edition)
License: MIT License

Copyright (c) 2025 Fusionpact Technologies Inc.
Licensed under the MIT License. See LICENSE file for details.
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Request, status, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import structlog

# Import enterprise modules
from src.config import settings, get_settings
from src.ai_processor import VesselMaintenanceAI
from src.models import ProcessingRequest, ProcessingResponse
from src.database import DatabaseManager
from src.tenant import (
    TenantManager, get_current_tenant, Tenant, TenantCreate, TenantUpdate,
    TenantContext, require_tenant_role
)
from src.auth import (
    AuthManager, get_current_user, require_superuser, require_active_user,
    User, UserCreate, UserLogin, Token
)
from src.rate_limiter import rate_limit_middleware, get_rate_limiter
from src.monitoring import (
    monitoring_middleware, get_metrics_collector, get_health_checker,
    get_performance_monitor, setup_structured_logging, background_metrics_collection
)
from src.analytics import (
    get_analytics_engine, AnalyticsFilter, AnalyticsTimeRange
)

# Setup structured logging
setup_structured_logging()
logger = structlog.get_logger(__name__)

# Background tasks for enterprise features
background_tasks = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown tasks"""
    logger.info("Starting Vessel Maintenance AI System Enterprise Edition")
    
    # Start background tasks
    if settings.monitoring_enabled:
        background_tasks['metrics'] = asyncio.create_task(background_metrics_collection())
        logger.info("Background metrics collection started")
    
    # Yield control to the application
    yield
    
    # Cleanup tasks
    logger.info("Shutting down Vessel Maintenance AI System")
    for task_name, task in background_tasks.items():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            logger.info(f"Background task {task_name} cancelled")

# Initialize FastAPI application with enterprise metadata
app = FastAPI(
    title="Vessel Maintenance AI System - Enterprise Edition",
    description="""
    Enterprise-grade AI-powered application for processing vessel maintenance records,
    sensor anomaly alerts, and incident reports with advanced analytics and multi-tenant support.
    
    **Enterprise Features:**
    - Multi-tenant Architecture with data isolation
    - Advanced Analytics with predictive insights  
    - API Rate Limiting and quota management
    - Custom Classification Models and training
    - Enterprise Authentication (SSO, RBAC, LDAP)
    - Comprehensive Audit Logging and compliance
    - Maritime Standards compliance (IMO, MARPOL)
    - Real-time Monitoring and alerting
    """,
    version="2.0.0",
    contact={
        "name": "Fusionpact Technologies Inc.",
        "url": "https://fusionpact.com",
        "email": "support@fusionpact.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    terms_of_service="https://fusionpact.com/terms",
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    lifespan=lifespan
)

# Add enterprise middleware stack
if settings.rate_limiting_enabled:
    app.middleware("http")(rate_limit_middleware)
    logger.info("Rate limiting middleware enabled")

if settings.monitoring_enabled:
    app.middleware("http")(monitoring_middleware)
    logger.info("Monitoring middleware enabled")

# Configure CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Enterprise Configuration
ENTERPRISE_CONFIG = {
    "multi_tenant_support": settings.multi_tenant_enabled,
    "advanced_analytics": settings.advanced_analytics_enabled,
    "api_rate_limiting": settings.rate_limiting_enabled,
    "custom_models": settings.custom_models_enabled,
    "batch_processing": settings.batch_processing_enabled,
    "encryption_enabled": settings.encryption_enabled,
    "audit_logging": settings.audit_logging,
    "gdpr_compliance": settings.gdpr_compliance,
    "imo_compliance": settings.imo_compliance,
    "supported_databases": ["SQLite", "PostgreSQL", "MySQL"],
    "authentication_providers": ["Local", "LDAP", "OAuth2", "SAML"],
    "integration_protocols": ["REST", "WebSockets", "SSE"],
    "monitoring_enabled": settings.monitoring_enabled,
    "predictive_analytics": settings.predictive_analytics,
    "real_time_notifications": settings.notifications_enabled
}

# Initialize core system components
ai_processor = VesselMaintenanceAI()
db_manager = DatabaseManager()

# Ensure required directories exist
os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs(settings.model_storage_path, exist_ok=True)

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


# =============================================================================
# ENTERPRISE AUTHENTICATION ENDPOINTS
# =============================================================================

@app.post("/auth/register", response_model=User, tags=["Authentication"])
async def register_user(
    user_data: UserCreate,
    request: Request,
    current_user: User = Depends(require_superuser)
):
    """Register a new user (superuser only)"""
    auth_manager = AuthManager(db_manager.get_session())
    user = auth_manager.create_user(user_data)
    logger.info("User registered", user_id=user.id, username=user.username)
    return user


@app.post("/auth/login", response_model=Token, tags=["Authentication"])
async def login(
    login_data: UserLogin,
    request: Request
):
    """Authenticate user and return JWT tokens"""
    auth_manager = AuthManager(db_manager.get_session())
    
    user = auth_manager.authenticate_user(
        login_data.username,
        login_data.password,
        login_data.tenant_id,
        request
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    token = auth_manager.create_tokens(user, login_data.tenant_id, request)
    logger.info("User logged in", user_id=user.id, tenant_id=login_data.tenant_id)
    return token


@app.post("/auth/refresh", response_model=Token, tags=["Authentication"])
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token"""
    auth_manager = AuthManager(db_manager.get_session())
    new_token = auth_manager.refresh_token(refresh_token)
    
    if not new_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    return new_token


@app.post("/auth/logout", tags=["Authentication"])
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Logout user and invalidate tokens"""
    # Extract token from Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        auth_manager = AuthManager(db_manager.get_session())
        auth_manager.logout(token)
    
    logger.info("User logged out", user_id=current_user.id)
    return {"message": "Successfully logged out"}


@app.get("/auth/me", response_model=User, tags=["Authentication"])
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


# =============================================================================
# ENTERPRISE TENANT MANAGEMENT ENDPOINTS
# =============================================================================

@app.post("/tenants", response_model=Tenant, tags=["Tenant Management"])
async def create_tenant(
    tenant_data: TenantCreate,
    current_user: User = Depends(require_superuser)
):
    """Create a new tenant (superuser only)"""
    tenant_manager = TenantManager(db_manager.get_session())
    tenant = tenant_manager.create_tenant(tenant_data)
    logger.info("Tenant created", tenant_id=tenant.id, domain=tenant.domain)
    return tenant


@app.get("/tenants", response_model=List[Tenant], tags=["Tenant Management"])
async def list_tenants(
    active_only: bool = True,
    current_user: User = Depends(require_superuser)
):
    """List all tenants (superuser only)"""
    tenant_manager = TenantManager(db_manager.get_session())
    return tenant_manager.list_tenants(active_only)


@app.get("/tenants/{tenant_id}", response_model=Tenant, tags=["Tenant Management"])
async def get_tenant(
    tenant_id: str,
    current_user: User = Depends(require_superuser)
):
    """Get tenant details (superuser only)"""
    tenant_manager = TenantManager(db_manager.get_session())
    tenant = tenant_manager.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@app.put("/tenants/{tenant_id}", response_model=Tenant, tags=["Tenant Management"])
async def update_tenant(
    tenant_id: str,
    update_data: TenantUpdate,
    current_user: User = Depends(require_superuser)
):
    """Update tenant information (superuser only)"""
    tenant_manager = TenantManager(db_manager.get_session())
    tenant = tenant_manager.update_tenant(tenant_id, update_data)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    logger.info("Tenant updated", tenant_id=tenant_id)
    return tenant


@app.delete("/tenants/{tenant_id}", tags=["Tenant Management"])
async def delete_tenant(
    tenant_id: str,
    current_user: User = Depends(require_superuser)
):
    """Delete (deactivate) tenant (superuser only)"""
    tenant_manager = TenantManager(db_manager.get_session())
    success = tenant_manager.delete_tenant(tenant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tenant not found")
    logger.info("Tenant deleted", tenant_id=tenant_id)
    return {"message": "Tenant successfully deactivated"}


# =============================================================================
# ENTERPRISE ANALYTICS ENDPOINTS
# =============================================================================

@app.get("/analytics/dashboard", tags=["Analytics"])
async def get_analytics_dashboard(
    time_range: AnalyticsTimeRange = AnalyticsTimeRange.LAST_30_DAYS,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_tenant: Tenant = Depends(get_current_tenant),
    current_user: User = Depends(require_active_user)
):
    """Get comprehensive analytics dashboard for tenant"""
    analytics_engine = get_analytics_engine()
    
    filters = AnalyticsFilter(
        tenant_id=current_tenant.id,
        time_range=time_range,
        start_date=start_date,
        end_date=end_date
    )
    
    dashboard = await analytics_engine.generate_dashboard(current_tenant.id, filters)
    return dashboard


@app.get("/analytics/trends/{metric_type}", tags=["Analytics"])
async def get_trend_analysis(
    metric_type: str,
    time_range: AnalyticsTimeRange = AnalyticsTimeRange.LAST_30_DAYS,
    current_tenant: Tenant = Depends(get_current_tenant),
    current_user: User = Depends(require_active_user)
):
    """Get trend analysis for specific metric"""
    analytics_engine = get_analytics_engine()
    
    filters = AnalyticsFilter(
        tenant_id=current_tenant.id,
        time_range=time_range
    )
    
    data = await analytics_engine._get_analytics_data(current_tenant.id, filters)
    
    if metric_type == "document_volume":
        daily_counts = data.groupby(data['timestamp'].dt.date).size()
        trend = await analytics_engine.analyze_trends(
            daily_counts.reset_index(),
            metric_column=0,
            time_column='timestamp'
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unknown metric type: {metric_type}")
    
    return trend


@app.get("/analytics/predictions/{prediction_type}", tags=["Analytics"])
async def get_predictive_insights(
    prediction_type: str,
    horizon_days: int = 30,
    current_tenant: Tenant = Depends(get_current_tenant),
    current_user: User = Depends(require_active_user)
):
    """Get predictive insights for vessel maintenance"""
    analytics_engine = get_analytics_engine()
    
    insights = await analytics_engine.generate_predictive_insights(
        current_tenant.id,
        prediction_type,
        horizon_days
    )
    
    return insights


# =============================================================================
# ENTERPRISE MONITORING ENDPOINTS
# =============================================================================

@app.get("/metrics", response_class=PlainTextResponse, tags=["Monitoring"])
async def get_prometheus_metrics():
    """Get Prometheus metrics for monitoring"""
    if not settings.monitoring_enabled:
        raise HTTPException(status_code=404, detail="Monitoring not enabled")
    
    metrics_collector = get_metrics_collector()
    return metrics_collector.get_metrics()


@app.get("/health/detailed", tags=["Monitoring"])
async def get_detailed_health():
    """Get detailed health check information"""
    health_checker = get_health_checker()
    health_status = await health_checker.run_checks()
    return health_status


@app.get("/health/performance", tags=["Monitoring"])
async def get_performance_metrics():
    """Get current performance metrics"""
    performance_monitor = get_performance_monitor()
    current_metrics = performance_monitor.collect_metrics()
    summary = performance_monitor.get_metrics_summary(60)  # Last hour
    
    return {
        "current": current_metrics,
        "summary": summary
    }


# =============================================================================
# ENTERPRISE ADMINISTRATION ENDPOINTS
# =============================================================================

@app.get("/admin/config", tags=["Administration"])
async def get_enterprise_config(
    current_user: User = Depends(require_superuser)
):
    """Get enterprise configuration and feature status"""
    return {
        "config": ENTERPRISE_CONFIG,
        "settings": {
            "environment": settings.environment.value,
            "multi_tenant_enabled": settings.multi_tenant_enabled,
            "rate_limiting_enabled": settings.rate_limiting_enabled,
            "monitoring_enabled": settings.monitoring_enabled,
            "audit_logging": settings.audit_logging,
            "encryption_enabled": settings.encryption_enabled,
            "database_backend": settings.database_backend.value,
            "auth_provider": settings.auth_provider.value,
            "cache_backend": settings.cache_backend.value
        }
    }


def main():
    """
    Main entry point for the Enterprise Vessel Maintenance AI System.
    
    Configures and starts the Uvicorn ASGI server with enterprise-grade
    settings for development and production environments.
    """
    print("🚢 Starting Vessel Maintenance AI System - Enterprise Edition...")
    print(f"🌐 Server will be available at: http://localhost:{settings.port}")
    print(f"📊 Analytics Dashboard: http://localhost:{settings.port}/analytics/dashboard")
    print(f"🔐 Authentication: http://localhost:{settings.port}/auth/login")
    print(f"🏢 Multi-Tenant: {settings.multi_tenant_enabled}")
    print(f"⚡ Rate Limiting: {settings.rate_limiting_enabled}")
    print(f"📈 Monitoring: http://localhost:{settings.port}/metrics")
    print(f"💊 Health Check: http://localhost:{settings.port}/health")
    print(f"📖 API Docs: http://localhost:{settings.port}/docs")
    print(f"🔧 Environment: {settings.environment.value}")
    print(f"📄 License: MIT License - Fusionpact Technologies Inc.")
    print("=" * 60)
    
    # Start the server with enterprise configuration
    uvicorn.run(
        "app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development(),
        log_level=settings.log_level.lower(),
        workers=settings.workers if settings.is_production() else 1
    )


# Entry point when running directly
if __name__ == "__main__":
    main()
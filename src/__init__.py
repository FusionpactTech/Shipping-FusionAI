"""
Vessel Maintenance AI System

AI-powered application for automated processing and classification of 
vessel maintenance records, sensor anomaly alerts, and incident reports.

Copyright (c) 2025 Fusionpact Technologies Inc.
Licensed under the MIT License.
"""

__version__ = "1.0.0"
__author__ = "Fusionpact Technologies Inc."
__email__ = "support@fusionpact.com"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2025 Fusionpact Technologies Inc."

# Package metadata
__title__ = "vessel-maintenance-ai"
__description__ = "AI-powered application for maritime vessel maintenance processing"
__url__ = "https://github.com/FusionpactTech/Shipping-FusionAI"

# Import main components for easy access
from .ai_processor import VesselMaintenanceAI
from .database import DatabaseManager
from .models import (
    ClassificationType,
    PriorityLevel,
    DocumentType,
    ProcessingRequest,
    ProcessingResponse,
    AnalyticsData,
    FileUploadResponse,
    SystemStatus
)

# Export public API
__all__ = [
    # Core classes
    "VesselMaintenanceAI",
    "DatabaseManager",
    
    # Enums
    "ClassificationType", 
    "PriorityLevel",
    "DocumentType",
    
    # Models
    "ProcessingRequest",
    "ProcessingResponse", 
    "AnalyticsData",
    "FileUploadResponse",
    "SystemStatus",
    
    # Package metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__copyright__"
]
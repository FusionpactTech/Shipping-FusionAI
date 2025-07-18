"""
Vessel Maintenance AI System - Data Models

This module defines the data models and schemas used throughout the vessel
maintenance AI system. It provides type-safe data structures for requests,
responses, and internal data handling using Pydantic models.

Key Components:
- Classification and priority enumerations
- Request/response models for API endpoints
- Data validation and serialization
- Type hints for improved code safety

Author: AI Assistant
Date: 2025-07-18
Version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ClassificationType(str, Enum):
    """
    Enumeration of vessel maintenance document classification types.
    
    These classifications represent the main categories that documents
    can be automatically assigned to based on their content analysis.
    Each classification triggers specific workflows and response procedures.
    """
    CRITICAL_EQUIPMENT_FAILURE = "Critical Equipment Failure Risk"
    NAVIGATIONAL_HAZARD = "Navigational Hazard Alert"
    ENVIRONMENTAL_COMPLIANCE = "Environmental Compliance Breach"
    ROUTINE_MAINTENANCE = "Routine Maintenance Required"
    SAFETY_VIOLATION = "Safety Violation Detected"
    FUEL_EFFICIENCY = "Fuel Efficiency Alert"


class PriorityLevel(str, Enum):
    """
    Enumeration of priority levels for vessel maintenance issues.
    
    Priority levels determine the urgency of response required:
    - CRITICAL: Immediate action required (0-1 hours)
    - HIGH: Action required within 24 hours
    - MEDIUM: Action required within 72 hours
    - LOW: Can be scheduled during next maintenance window
    """
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class DocumentType(str, Enum):
    """
    Enumeration of document types that can be processed by the system.
    
    These types help the AI processor understand the context and
    apply appropriate analysis techniques for each document category.
    """
    MAINTENANCE_RECORD = "Maintenance Record"
    SENSOR_ALERT = "Sensor Alert"
    INCIDENT_REPORT = "Incident Report"
    INSPECTION_REPORT = "Inspection Report"
    COMPLIANCE_DOCUMENT = "Compliance Document"


class KeywordPattern(BaseModel):
    """
    Model representing a keyword pattern used for document classification.
    
    This model defines the structure for pattern-based classification rules
    that help the AI processor identify document types and assign priorities.
    
    Attributes:
        pattern (str): Regular expression pattern to match
        classification (ClassificationType): Target classification for matches
        priority (PriorityLevel): Priority level to assign
        weight (float): Importance weight for this pattern (0.0-2.0)
    """
    pattern: str = Field(..., description="Regular expression pattern for matching")
    classification: ClassificationType = Field(..., description="Target classification")
    priority: PriorityLevel = Field(..., description="Priority level to assign")
    weight: float = Field(default=1.0, ge=0.0, le=2.0, description="Pattern importance weight")


class ProcessingRequest(BaseModel):
    """
    Model for incoming document processing requests.
    
    This model validates and structures the data sent to the AI processor
    for document analysis. It ensures all required fields are present
    and properly formatted.
    
    Attributes:
        text (str): The document text content to be analyzed
        document_type (Optional[str]): Hint for document type (if known)
        vessel_id (Optional[str]): Identifier for the vessel (if applicable)
        metadata (Optional[Dict]): Additional context information
    """
    text: str = Field(..., min_length=10, description="Document text content to analyze")
    document_type: Optional[str] = Field(None, description="Document type hint")
    vessel_id: Optional[str] = Field(None, description="Vessel identifier")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class ProcessingResponse(BaseModel):
    """
    Model for AI processing results returned to clients.
    
    This model structures the comprehensive analysis results from the AI
    processor, including classification, priority assessment, extracted
    entities, and actionable recommendations.
    
    Attributes:
        id (str): Unique identifier for this processing result
        summary (str): Concise summary of the document content
        details (str): Detailed analysis and explanation
        classification (str): Assigned document classification
        priority (str): Determined priority level
        confidence_score (float): AI confidence in the classification (0.0-1.0)
        keywords (List[str]): Extracted keywords and key phrases
        entities (Dict): Categorized entities found in the text
        recommended_actions (List[str]): Actionable recommendations
        risk_assessment (str): Risk level and impact assessment
        document_type (Optional[str]): Detected or provided document type
        vessel_id (Optional[str]): Associated vessel identifier
        timestamp (datetime): When the processing was completed
        metadata (Dict): Additional processing metadata
    """
    id: str = Field(..., description="Unique processing result identifier")
    summary: str = Field(..., description="Concise document summary")
    details: str = Field(..., description="Detailed analysis explanation")
    classification: str = Field(..., description="Document classification")
    priority: str = Field(..., description="Assigned priority level")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Classification confidence")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    entities: Dict[str, List[str]] = Field(default_factory=dict, description="Categorized entities")
    recommended_actions: List[str] = Field(default_factory=list, description="Recommended actions")
    risk_assessment: str = Field(..., description="Risk assessment summary")
    document_type: Optional[str] = Field(None, description="Document type")
    vessel_id: Optional[str] = Field(None, description="Vessel identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="Processing timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Processing metadata")


class AnalyticsData(BaseModel):
    """
    Model for system analytics and reporting data.
    
    This model structures analytical data about system performance,
    processing statistics, and operational metrics for monitoring
    and reporting purposes.
    
    Attributes:
        total_processed (int): Total number of documents processed
        critical_alerts (int): Number of critical priority items identified
        classification_breakdown (Dict): Count by classification type
        priority_breakdown (Dict): Count by priority level
        recent_trends (List): Recent processing activity trends
        average_processing_time (Optional[float]): Average processing time in milliseconds
        system_performance (Optional[Dict]): System performance metrics
    """
    total_processed: int = Field(default=0, description="Total documents processed")
    critical_alerts: int = Field(default=0, description="Critical alerts identified")
    classification_breakdown: Dict[str, int] = Field(
        default_factory=dict, 
        description="Document count by classification"
    )
    priority_breakdown: Dict[str, int] = Field(
        default_factory=dict, 
        description="Document count by priority"
    )
    recent_trends: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="Recent processing trends"
    )
    average_processing_time: Optional[float] = Field(
        None, 
        description="Average processing time in milliseconds"
    )
    system_performance: Optional[Dict[str, Any]] = Field(
        None, 
        description="System performance metrics"
    )


class FileUploadResponse(BaseModel):
    """
    Model for file upload processing responses.
    
    This model structures the response when files are uploaded and
    processed through the system, providing feedback on the upload
    status and processing results.
    
    Attributes:
        filename (str): Name of the uploaded file
        file_size (int): Size of the uploaded file in bytes
        processing_status (str): Status of the processing operation
        results (List[ProcessingResponse]): Processing results for the file
        errors (List[str]): Any errors encountered during processing
    """
    filename: str = Field(..., description="Uploaded filename")
    file_size: int = Field(..., description="File size in bytes")
    processing_status: str = Field(..., description="Processing status")
    results: List[ProcessingResponse] = Field(default_factory=list, description="Processing results")
    errors: List[str] = Field(default_factory=list, description="Processing errors")


class SystemStatus(BaseModel):
    """
    Model for system health and status information.
    
    This model provides information about the current state of the
    vessel maintenance AI system, including operational status,
    performance metrics, and health indicators.
    
    Attributes:
        status (str): Overall system status (online, offline, degraded)
        version (str): System version information
        uptime (float): System uptime in seconds
        processed_today (int): Documents processed today
        queue_size (int): Current processing queue size
        memory_usage (Optional[float]): Memory usage percentage
        cpu_usage (Optional[float]): CPU usage percentage
        last_health_check (datetime): Timestamp of last health check
    """
    status: str = Field(..., description="System operational status")
    version: str = Field(default="1.0.0", description="System version")
    uptime: float = Field(..., description="System uptime in seconds")
    processed_today: int = Field(default=0, description="Documents processed today")
    queue_size: int = Field(default=0, description="Processing queue size")
    memory_usage: Optional[float] = Field(None, description="Memory usage percentage")
    cpu_usage: Optional[float] = Field(None, description="CPU usage percentage")
    last_health_check: datetime = Field(
        default_factory=datetime.now, 
        description="Last health check timestamp"
    )
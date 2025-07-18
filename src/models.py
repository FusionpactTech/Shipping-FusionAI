from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ClassificationType(str, Enum):
    CRITICAL_EQUIPMENT_FAILURE = "Critical Equipment Failure Risk"
    NAVIGATIONAL_HAZARD = "Navigational Hazard Alert"
    ENVIRONMENTAL_COMPLIANCE = "Environmental Compliance Breach"
    ROUTINE_MAINTENANCE = "Routine Maintenance Required"
    SAFETY_VIOLATION = "Safety Violation Detected"
    FUEL_EFFICIENCY = "Fuel Efficiency Alert"

class PriorityLevel(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class DocumentType(str, Enum):
    MAINTENANCE_RECORD = "Maintenance Record"
    SENSOR_ALERT = "Sensor Alert"
    INCIDENT_REPORT = "Incident Report"
    INSPECTION_REPORT = "Inspection Report"
    COMPLIANCE_DOCUMENT = "Compliance Document"

class ProcessingRequest(BaseModel):
    text: str = Field(..., description="Text content to be processed")
    document_type: Optional[DocumentType] = Field(None, description="Type of document being processed")
    vessel_id: Optional[str] = Field(None, description="Vessel identifier")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

class ProcessingResponse(BaseModel):
    id: Optional[str] = Field(None, description="Unique identifier for the processing result")
    summary: str = Field(..., description="AI-generated summary of the content")
    details: str = Field(..., description="Detailed analysis and findings")
    classification: ClassificationType = Field(..., description="Classified action category")
    priority: PriorityLevel = Field(..., description="Priority level of the issue")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the classification")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    entities: Dict[str, List[str]] = Field(default_factory=dict, description="Named entities extracted")
    recommended_actions: List[str] = Field(default_factory=list, description="Recommended actions to take")
    risk_assessment: str = Field(..., description="Risk assessment and potential impact")
    document_type: Optional[DocumentType] = Field(None, description="Detected document type")
    vessel_id: Optional[str] = Field(None, description="Associated vessel identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="Processing timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class AnalyticsData(BaseModel):
    total_processed: int = Field(..., description="Total documents processed")
    critical_alerts: int = Field(..., description="Number of critical alerts")
    classification_breakdown: Dict[str, int] = Field(..., description="Breakdown by classification type")
    priority_breakdown: Dict[str, int] = Field(..., description="Breakdown by priority level")
    recent_trends: List[Dict[str, Any]] = Field(..., description="Recent processing trends")
    vessel_stats: Dict[str, Any] = Field(default_factory=dict, description="Per-vessel statistics")

class KeywordPattern(BaseModel):
    pattern: str = Field(..., description="Regex pattern or keyword")
    classification: ClassificationType = Field(..., description="Associated classification")
    priority: PriorityLevel = Field(..., description="Associated priority level")
    weight: float = Field(default=1.0, description="Weight for scoring")

class VesselInfo(BaseModel):
    vessel_id: str = Field(..., description="Unique vessel identifier")
    name: str = Field(..., description="Vessel name")
    type: str = Field(..., description="Vessel type (cargo, passenger, etc.)")
    flag: Optional[str] = Field(None, description="Flag state")
    imo_number: Optional[str] = Field(None, description="IMO number")
    last_inspection: Optional[datetime] = Field(None, description="Last inspection date")
    status: str = Field(default="Active", description="Current vessel status")
    
class AlertRule(BaseModel):
    rule_id: str = Field(..., description="Unique rule identifier")
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    conditions: List[str] = Field(..., description="Conditions that trigger the rule")
    classification: ClassificationType = Field(..., description="Classification when rule is triggered")
    priority: PriorityLevel = Field(..., description="Priority when rule is triggered")
    actions: List[str] = Field(..., description="Actions to take when rule is triggered")
    is_active: bool = Field(default=True, description="Whether the rule is active")
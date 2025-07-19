"""
Enterprise Advanced Analytics Module

This module provides comprehensive analytics capabilities for the vessel
maintenance AI system, including trend analysis, predictive insights,
business intelligence, and advanced reporting features.

Author: Fusionpact Technologies Inc.
Date: 2025-01-27
Version: 2.0.0
License: MIT License
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import asyncio
from dataclasses import dataclass
from enum import Enum
import structlog

from .config import settings
from .models import ClassificationType, PriorityLevel
from .tenant import TenantContext

logger = structlog.get_logger(__name__)


class AnalyticsTimeRange(str, Enum):
    """Time range options for analytics"""
    LAST_24_HOURS = "24h"
    LAST_7_DAYS = "7d"
    LAST_30_DAYS = "30d"
    LAST_90_DAYS = "90d"
    LAST_6_MONTHS = "6m"
    LAST_YEAR = "1y"
    CUSTOM = "custom"


class TrendDirection(str, Enum):
    """Trend direction enumeration"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"


class MetricType(str, Enum):
    """Analytics metric types"""
    DOCUMENT_VOLUME = "document_volume"
    CLASSIFICATION_ACCURACY = "classification_accuracy"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    USER_ACTIVITY = "user_activity"
    PRIORITY_DISTRIBUTION = "priority_distribution"
    VESSEL_PERFORMANCE = "vessel_performance"


@dataclass
class TrendAnalysis:
    """Trend analysis result"""
    metric: str
    direction: TrendDirection
    change_percent: float
    confidence: float
    slope: float
    r_squared: float
    forecast_value: Optional[float] = None
    forecast_confidence_interval: Optional[Tuple[float, float]] = None


class AnalyticsFilter(BaseModel):
    """Analytics filter configuration"""
    tenant_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    time_range: Optional[AnalyticsTimeRange] = None
    classification_types: Optional[List[ClassificationType]] = None
    priority_levels: Optional[List[PriorityLevel]] = None
    vessel_ids: Optional[List[str]] = None
    user_ids: Optional[List[str]] = None
    document_types: Optional[List[str]] = None


class MetricSummary(BaseModel):
    """Summary statistics for a metric"""
    metric_name: str
    value: float
    previous_value: Optional[float] = None
    change_percent: Optional[float] = None
    trend: Optional[TrendDirection] = None
    unit: str = ""
    description: str = ""


class AnalyticsDashboard(BaseModel):
    """Analytics dashboard data model"""
    tenant_id: str
    generated_at: datetime
    time_range: AnalyticsTimeRange
    summary_metrics: List[MetricSummary]
    charts: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]


class PredictiveModel:
    """Base class for predictive analytics models"""
    
    def __init__(self, model_type: str):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = []
    
    def train(self, X: np.ndarray, y: np.ndarray, feature_names: List[str]):
        """Train the predictive model"""
        self.feature_names = feature_names
        X_scaled = self.scaler.fit_transform(X)
        
        if self.model_type == "linear_regression":
            self.model = LinearRegression()
        
        self.model.fit(X_scaled, y)
        self.is_trained = True
    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Make predictions with confidence intervals"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        
        # Simple confidence interval calculation
        # In a real implementation, you'd use more sophisticated methods
        residuals = np.std(predictions) * 0.2  # Simplified confidence calculation
        confidence_intervals = np.column_stack([
            predictions - residuals,
            predictions + residuals
        ])
        
        return predictions, confidence_intervals


class AdvancedAnalyticsEngine:
    """
    Comprehensive analytics engine for vessel maintenance insights.
    
    This class provides advanced analytics capabilities including trend analysis,
    predictive modeling, anomaly detection, and business intelligence reporting.
    """
    
    def __init__(self):
        self.predictive_models: Dict[str, PredictiveModel] = {}
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self._cache = {}
        self._cache_ttl = timedelta(minutes=15)
        self._last_cache_cleanup = datetime.utcnow()
    
    async def generate_dashboard(
        self,
        tenant_id: str,
        filters: AnalyticsFilter
    ) -> AnalyticsDashboard:
        """
        Generate comprehensive analytics dashboard for a tenant.
        
        Args:
            tenant_id: Tenant identifier
            filters: Analytics filters
            
        Returns:
            Complete dashboard with metrics, charts, and insights
        """
        logger.info("Generating analytics dashboard", tenant_id=tenant_id)
        
        # Set time range if not specified
        if not filters.time_range and not filters.start_date:
            filters.time_range = AnalyticsTimeRange.LAST_30_DAYS
            filters.end_date = datetime.utcnow()
            filters.start_date = filters.end_date - timedelta(days=30)
        elif filters.time_range and filters.time_range != AnalyticsTimeRange.CUSTOM:
            filters.end_date = datetime.utcnow()
            filters.start_date = self._get_start_date_for_range(filters.time_range)
        
        # Get data for analysis
        data = await self._get_analytics_data(tenant_id, filters)
        
        # Generate summary metrics
        summary_metrics = await self._generate_summary_metrics(data, filters)
        
        # Generate charts
        charts = await self._generate_charts(data, filters)
        
        # Generate insights and recommendations
        insights = await self._generate_insights(data, summary_metrics)
        recommendations = await self._generate_recommendations(data, insights)
        
        return AnalyticsDashboard(
            tenant_id=tenant_id,
            generated_at=datetime.utcnow(),
            time_range=filters.time_range or AnalyticsTimeRange.CUSTOM,
            summary_metrics=summary_metrics,
            charts=charts,
            insights=insights,
            recommendations=recommendations
        )
    
    async def analyze_trends(
        self,
        data: pd.DataFrame,
        metric_column: str,
        time_column: str = "timestamp"
    ) -> TrendAnalysis:
        """
        Perform comprehensive trend analysis on time series data.
        
        Args:
            data: DataFrame with time series data
            metric_column: Column name containing the metric values
            time_column: Column name containing timestamps
            
        Returns:
            Detailed trend analysis results
        """
        if data.empty or len(data) < 3:
            return TrendAnalysis(
                metric=metric_column,
                direction=TrendDirection.STABLE,
                change_percent=0.0,
                confidence=0.0,
                slope=0.0,
                r_squared=0.0
            )
        
        # Prepare data for regression
        data_sorted = data.sort_values(time_column)
        X = np.arange(len(data_sorted)).reshape(-1, 1)
        y = data_sorted[metric_column].values
        
        # Fit linear regression
        model = LinearRegression()
        model.fit(X, y)
        
        # Calculate metrics
        y_pred = model.predict(X)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        slope = model.coef_[0]
        
        # Determine trend direction
        if abs(slope) < np.std(y) * 0.1:
            direction = TrendDirection.STABLE
        elif slope > 0:
            direction = TrendDirection.INCREASING
        else:
            direction = TrendDirection.DECREASING
        
        # Check for volatility
        volatility = np.std(y - y_pred) / np.mean(y) if np.mean(y) != 0 else 0
        if volatility > 0.3:
            direction = TrendDirection.VOLATILE
        
        # Calculate percentage change
        if len(y) >= 2:
            change_percent = ((y[-1] - y[0]) / y[0] * 100) if y[0] != 0 else 0
        else:
            change_percent = 0.0
        
        # Forecast next value
        next_x = np.array([[len(data_sorted)]])
        forecast_value = model.predict(next_x)[0]
        
        # Simple confidence interval for forecast
        residual_std = np.std(y - y_pred)
        confidence_interval = (
            forecast_value - 1.96 * residual_std,
            forecast_value + 1.96 * residual_std
        )
        
        return TrendAnalysis(
            metric=metric_column,
            direction=direction,
            change_percent=change_percent,
            confidence=r_squared,
            slope=slope,
            r_squared=r_squared,
            forecast_value=forecast_value,
            forecast_confidence_interval=confidence_interval
        )
    
    async def detect_anomalies(
        self,
        data: pd.DataFrame,
        features: List[str]
    ) -> Tuple[np.ndarray, pd.DataFrame]:
        """
        Detect anomalies in vessel maintenance data.
        
        Args:
            data: DataFrame with feature data
            features: List of feature column names
            
        Returns:
            Tuple of (anomaly_scores, anomalous_records)
        """
        if data.empty or len(data) < 10:
            return np.array([]), pd.DataFrame()
        
        # Prepare feature data
        feature_data = data[features].fillna(0)
        
        # Fit anomaly detector
        self.anomaly_detector.fit(feature_data)
        
        # Predict anomalies
        anomaly_scores = self.anomaly_detector.decision_function(feature_data)
        anomaly_labels = self.anomaly_detector.predict(feature_data)
        
        # Get anomalous records
        anomalous_records = data[anomaly_labels == -1].copy()
        anomalous_records['anomaly_score'] = anomaly_scores[anomaly_labels == -1]
        
        return anomaly_scores, anomalous_records
    
    async def generate_predictive_insights(
        self,
        tenant_id: str,
        prediction_type: str,
        horizon_days: int = 30
    ) -> Dict[str, Any]:
        """
        Generate predictive insights for vessel maintenance.
        
        Args:
            tenant_id: Tenant identifier
            prediction_type: Type of prediction to make
            horizon_days: Prediction horizon in days
            
        Returns:
            Predictive insights and forecasts
        """
        # Get historical data
        filters = AnalyticsFilter(
            tenant_id=tenant_id,
            start_date=datetime.utcnow() - timedelta(days=365),
            end_date=datetime.utcnow()
        )
        data = await self._get_analytics_data(tenant_id, filters)
        
        insights = {}
        
        if prediction_type == "failure_risk":
            insights = await self._predict_failure_risk(data, horizon_days)
        elif prediction_type == "maintenance_demand":
            insights = await self._predict_maintenance_demand(data, horizon_days)
        elif prediction_type == "cost_forecast":
            insights = await self._predict_cost_forecast(data, horizon_days)
        
        return insights
    
    async def generate_vessel_performance_analysis(
        self,
        tenant_id: str,
        vessel_id: str,
        filters: AnalyticsFilter
    ) -> Dict[str, Any]:
        """
        Generate comprehensive vessel performance analysis.
        
        Args:
            tenant_id: Tenant identifier
            vessel_id: Vessel identifier
            filters: Analytics filters
            
        Returns:
            Detailed vessel performance analysis
        """
        filters.vessel_ids = [vessel_id]
        data = await self._get_analytics_data(tenant_id, filters)
        
        if data.empty:
            return {"error": "No data available for the specified vessel"}
        
        # Performance metrics
        performance_metrics = {
            "total_incidents": len(data),
            "critical_incidents": len(data[data.get('priority') == 'Critical']),
            "average_resolution_time": data.get('resolution_time', pd.Series()).mean(),
            "incident_frequency": len(data) / max(1, (filters.end_date - filters.start_date).days),
            "most_common_issues": data.get('classification', pd.Series()).value_counts().head(5).to_dict()
        }
        
        # Trend analysis
        trends = {}
        if 'timestamp' in data.columns:
            daily_incidents = data.groupby(data['timestamp'].dt.date).size()
            trends['incident_trend'] = await self.analyze_trends(
                daily_incidents.reset_index(),
                metric_column=0,
                time_column='timestamp'
            )
        
        # Efficiency scores
        efficiency_score = self._calculate_vessel_efficiency_score(data)
        
        return {
            "vessel_id": vessel_id,
            "analysis_period": {
                "start": filters.start_date,
                "end": filters.end_date
            },
            "performance_metrics": performance_metrics,
            "trends": trends,
            "efficiency_score": efficiency_score,
            "recommendations": self._generate_vessel_recommendations(data, efficiency_score)
        }
    
    async def _get_analytics_data(
        self,
        tenant_id: str,
        filters: AnalyticsFilter
    ) -> pd.DataFrame:
        """Get analytics data based on filters"""
        # This would query your actual database
        # For now, generating sample data
        
        cache_key = f"analytics_data_{tenant_id}_{filters.start_date}_{filters.end_date}"
        
        # Check cache
        if cache_key in self._cache:
            cache_entry = self._cache[cache_key]
            if datetime.utcnow() - cache_entry['timestamp'] < self._cache_ttl:
                return cache_entry['data']
        
        # Generate sample data for demonstration
        date_range = pd.date_range(
            start=filters.start_date,
            end=filters.end_date,
            freq='D'
        )
        
        np.random.seed(42)  # For reproducible results
        
        data = []
        for date in date_range:
            num_records = np.random.poisson(10)  # Average 10 records per day
            
            for _ in range(num_records):
                record = {
                    'timestamp': date + timedelta(
                        hours=np.random.randint(0, 24),
                        minutes=np.random.randint(0, 60)
                    ),
                    'tenant_id': tenant_id,
                    'vessel_id': f"vessel_{np.random.randint(1, 21)}",
                    'classification': np.random.choice([
                        'Critical Equipment Failure Risk',
                        'Routine Maintenance Required',
                        'Safety Violation Detected',
                        'Environmental Compliance Breach',
                        'Fuel Efficiency Alert'
                    ]),
                    'priority': np.random.choice(['Critical', 'High', 'Medium', 'Low']),
                    'confidence_score': np.random.uniform(0.7, 1.0),
                    'resolution_time': np.random.exponential(24),  # Hours
                    'cost_estimate': np.random.lognormal(8, 1)  # Dollars
                }
                data.append(record)
        
        df = pd.DataFrame(data)
        
        # Cache the result
        self._cache[cache_key] = {
            'data': df,
            'timestamp': datetime.utcnow()
        }
        
        # Cleanup old cache entries
        if datetime.utcnow() - self._last_cache_cleanup > timedelta(hours=1):
            await self._cleanup_cache()
        
        return df
    
    async def _generate_summary_metrics(
        self,
        data: pd.DataFrame,
        filters: AnalyticsFilter
    ) -> List[MetricSummary]:
        """Generate summary metrics for the dashboard"""
        metrics = []
        
        if data.empty:
            return metrics
        
        # Total documents processed
        total_docs = len(data)
        metrics.append(MetricSummary(
            metric_name="Total Documents Processed",
            value=total_docs,
            unit="documents",
            description="Total number of documents processed in the selected period"
        ))
        
        # Critical incidents
        critical_count = len(data[data['priority'] == 'Critical'])
        critical_percentage = (critical_count / total_docs * 100) if total_docs > 0 else 0
        metrics.append(MetricSummary(
            metric_name="Critical Incidents",
            value=critical_count,
            change_percent=critical_percentage,
            unit="incidents",
            description="Number of critical priority incidents identified"
        ))
        
        # Average confidence score
        avg_confidence = data['confidence_score'].mean()
        metrics.append(MetricSummary(
            metric_name="Average AI Confidence",
            value=round(avg_confidence, 2),
            unit="score",
            description="Average confidence score of AI classifications"
        ))
        
        # Average resolution time
        avg_resolution = data['resolution_time'].mean()
        metrics.append(MetricSummary(
            metric_name="Average Resolution Time",
            value=round(avg_resolution, 1),
            unit="hours",
            description="Average time to resolve incidents"
        ))
        
        # Cost estimates
        total_cost = data['cost_estimate'].sum()
        metrics.append(MetricSummary(
            metric_name="Total Estimated Costs",
            value=round(total_cost, 2),
            unit="USD",
            description="Total estimated costs for identified issues"
        ))
        
        return metrics
    
    async def _generate_charts(
        self,
        data: pd.DataFrame,
        filters: AnalyticsFilter
    ) -> Dict[str, Any]:
        """Generate chart data for the dashboard"""
        charts = {}
        
        if data.empty:
            return charts
        
        # Time series chart of daily document processing
        daily_counts = data.groupby(data['timestamp'].dt.date).size()
        charts['daily_processing'] = {
            'type': 'line',
            'data': {
                'x': daily_counts.index.astype(str).tolist(),
                'y': daily_counts.values.tolist()
            },
            'title': 'Daily Document Processing Volume',
            'x_label': 'Date',
            'y_label': 'Number of Documents'
        }
        
        # Priority distribution pie chart
        priority_counts = data['priority'].value_counts()
        charts['priority_distribution'] = {
            'type': 'pie',
            'data': {
                'labels': priority_counts.index.tolist(),
                'values': priority_counts.values.tolist()
            },
            'title': 'Priority Level Distribution'
        }
        
        # Classification breakdown bar chart
        classification_counts = data['classification'].value_counts().head(10)
        charts['classification_breakdown'] = {
            'type': 'bar',
            'data': {
                'x': classification_counts.index.tolist(),
                'y': classification_counts.values.tolist()
            },
            'title': 'Top Issue Classifications',
            'x_label': 'Classification Type',
            'y_label': 'Number of Incidents'
        }
        
        # Confidence score distribution histogram
        charts['confidence_distribution'] = {
            'type': 'histogram',
            'data': {
                'values': data['confidence_score'].tolist(),
                'bins': 20
            },
            'title': 'AI Confidence Score Distribution',
            'x_label': 'Confidence Score',
            'y_label': 'Frequency'
        }
        
        # Vessel performance heatmap
        vessel_metrics = data.groupby('vessel_id').agg({
            'priority': lambda x: (x == 'Critical').sum(),
            'resolution_time': 'mean',
            'cost_estimate': 'sum'
        }).fillna(0)
        
        charts['vessel_heatmap'] = {
            'type': 'heatmap',
            'data': {
                'vessels': vessel_metrics.index.tolist(),
                'metrics': ['Critical Incidents', 'Avg Resolution Time', 'Total Cost'],
                'values': vessel_metrics.values.tolist()
            },
            'title': 'Vessel Performance Heatmap'
        }
        
        return charts
    
    async def _generate_insights(
        self,
        data: pd.DataFrame,
        metrics: List[MetricSummary]
    ) -> List[str]:
        """Generate actionable insights from the data"""
        insights = []
        
        if data.empty:
            return insights
        
        # Analyze trends
        if len(data) > 7:  # Need at least a week of data
            daily_counts = data.groupby(data['timestamp'].dt.date).size()
            trend_analysis = await self.analyze_trends(
                daily_counts.reset_index(),
                metric_column=0,
                time_column='timestamp'
            )
            
            if trend_analysis.direction == TrendDirection.INCREASING:
                insights.append(
                    f"Document processing volume is increasing by {trend_analysis.change_percent:.1f}% "
                    f"over the analysis period. Consider scaling resources."
                )
            elif trend_analysis.direction == TrendDirection.DECREASING:
                insights.append(
                    f"Document processing volume is decreasing by {trend_analysis.change_percent:.1f}% "
                    f"over the analysis period. This may indicate improved vessel performance."
                )
        
        # Critical incident analysis
        critical_rate = len(data[data['priority'] == 'Critical']) / len(data)
        if critical_rate > 0.15:  # More than 15% critical
            insights.append(
                f"High critical incident rate ({critical_rate:.1%}). "
                f"Focus on proactive maintenance to reduce emergency situations."
            )
        
        # Confidence score analysis
        low_confidence = len(data[data['confidence_score'] < 0.8]) / len(data)
        if low_confidence > 0.20:  # More than 20% low confidence
            insights.append(
                f"AI model shows low confidence in {low_confidence:.1%} of classifications. "
                f"Consider retraining with more diverse data."
            )
        
        # Vessel-specific insights
        vessel_incident_counts = data['vessel_id'].value_counts()
        high_incident_vessels = vessel_incident_counts[vessel_incident_counts > vessel_incident_counts.mean() + 2 * vessel_incident_counts.std()]
        
        if len(high_incident_vessels) > 0:
            insights.append(
                f"Vessels {', '.join(high_incident_vessels.index[:3])} show unusually high incident rates. "
                f"Recommend detailed maintenance review."
            )
        
        # Cost analysis
        high_cost_incidents = data[data['cost_estimate'] > data['cost_estimate'].quantile(0.9)]
        if len(high_cost_incidents) > 0:
            top_cost_classification = high_cost_incidents['classification'].mode().iloc[0]
            insights.append(
                f"'{top_cost_classification}' incidents account for the highest estimated costs. "
                f"Prioritize preventive measures for this issue type."
            )
        
        return insights
    
    async def _generate_recommendations(
        self,
        data: pd.DataFrame,
        insights: List[str]
    ) -> List[str]:
        """Generate actionable recommendations based on insights"""
        recommendations = []
        
        if data.empty:
            return recommendations
        
        # Recommendations based on priority distribution
        priority_dist = data['priority'].value_counts(normalize=True)
        
        if priority_dist.get('Critical', 0) > 0.1:
            recommendations.append(
                "Implement predictive maintenance schedules to reduce critical incidents"
            )
        
        if priority_dist.get('Low', 0) < 0.3:
            recommendations.append(
                "Increase monitoring frequency to catch issues before they become critical"
            )
        
        # Recommendations based on resolution times
        avg_resolution = data['resolution_time'].mean()
        if avg_resolution > 48:  # More than 48 hours
            recommendations.append(
                "Establish rapid response teams to reduce average resolution time"
            )
        
        # Recommendations based on vessel performance
        vessel_performance = data.groupby('vessel_id')['priority'].apply(
            lambda x: (x == 'Critical').sum()
        )
        underperforming_vessels = vessel_performance[vessel_performance > vessel_performance.mean() + vessel_performance.std()]
        
        if len(underperforming_vessels) > 0:
            recommendations.append(
                f"Schedule comprehensive maintenance reviews for vessels: {', '.join(underperforming_vessels.index[:5])}"
            )
        
        # AI model recommendations
        low_confidence_rate = (data['confidence_score'] < 0.8).mean()
        if low_confidence_rate > 0.2:
            recommendations.append(
                "Enhance AI model training with additional labeled data to improve classification confidence"
            )
        
        # Cost optimization recommendations
        cost_by_classification = data.groupby('classification')['cost_estimate'].sum().sort_values(ascending=False)
        top_cost_driver = cost_by_classification.index[0]
        recommendations.append(
            f"Focus cost reduction efforts on '{top_cost_driver}' incidents - highest total cost driver"
        )
        
        return recommendations
    
    def _get_start_date_for_range(self, time_range: AnalyticsTimeRange) -> datetime:
        """Convert time range enum to start date"""
        now = datetime.utcnow()
        
        if time_range == AnalyticsTimeRange.LAST_24_HOURS:
            return now - timedelta(hours=24)
        elif time_range == AnalyticsTimeRange.LAST_7_DAYS:
            return now - timedelta(days=7)
        elif time_range == AnalyticsTimeRange.LAST_30_DAYS:
            return now - timedelta(days=30)
        elif time_range == AnalyticsTimeRange.LAST_90_DAYS:
            return now - timedelta(days=90)
        elif time_range == AnalyticsTimeRange.LAST_6_MONTHS:
            return now - timedelta(days=180)
        elif time_range == AnalyticsTimeRange.LAST_YEAR:
            return now - timedelta(days=365)
        else:
            return now - timedelta(days=30)  # Default to 30 days
    
    def _calculate_vessel_efficiency_score(self, data: pd.DataFrame) -> float:
        """Calculate overall vessel efficiency score"""
        if data.empty:
            return 0.0
        
        # Factors that contribute to efficiency score
        critical_penalty = len(data[data['priority'] == 'Critical']) / len(data) * 40
        resolution_penalty = min(data['resolution_time'].mean() / 24, 5) * 10  # Cap at 5 days
        confidence_bonus = data['confidence_score'].mean() * 20
        
        # Base score of 100, subtract penalties, add bonuses
        score = max(0, 100 - critical_penalty - resolution_penalty + confidence_bonus - 100)
        return min(100, score)  # Cap at 100
    
    def _generate_vessel_recommendations(self, data: pd.DataFrame, efficiency_score: float) -> List[str]:
        """Generate vessel-specific recommendations"""
        recommendations = []
        
        if efficiency_score < 50:
            recommendations.append("Immediate maintenance review required - efficiency score below acceptable threshold")
        elif efficiency_score < 70:
            recommendations.append("Schedule preventive maintenance - efficiency declining")
        
        # Issue-specific recommendations
        top_issues = data['classification'].value_counts().head(3)
        for issue, count in top_issues.items():
            if count > len(data) * 0.3:  # More than 30% of incidents
                recommendations.append(f"Address recurring '{issue}' - represents {count/len(data):.1%} of all incidents")
        
        return recommendations
    
    async def _predict_failure_risk(self, data: pd.DataFrame, horizon_days: int) -> Dict[str, Any]:
        """Predict failure risk for the next period"""
        # This is a simplified prediction model
        # In a real implementation, you'd use more sophisticated ML models
        
        if data.empty:
            return {"error": "Insufficient data for prediction"}
        
        # Calculate failure rate trends
        daily_failures = data[data['priority'] == 'Critical'].groupby(data['timestamp'].dt.date).size()
        
        if len(daily_failures) < 7:
            return {"error": "Need at least 7 days of data for prediction"}
        
        # Simple linear prediction
        trend_analysis = await self.analyze_trends(
            daily_failures.reset_index(),
            metric_column=0,
            time_column='timestamp'
        )
        
        # Predict for horizon
        predicted_failures = max(0, trend_analysis.forecast_value * horizon_days)
        
        return {
            "prediction_horizon_days": horizon_days,
            "predicted_critical_failures": round(predicted_failures),
            "confidence": trend_analysis.confidence,
            "trend_direction": trend_analysis.direction.value,
            "risk_level": "high" if predicted_failures > daily_failures.mean() * horizon_days * 1.5 else "moderate"
        }
    
    async def _predict_maintenance_demand(self, data: pd.DataFrame, horizon_days: int) -> Dict[str, Any]:
        """Predict maintenance demand for the next period"""
        if data.empty:
            return {"error": "Insufficient data for prediction"}
        
        # Analyze maintenance patterns
        maintenance_incidents = data[data['classification'].str.contains('Maintenance', na=False)]
        daily_maintenance = maintenance_incidents.groupby(data['timestamp'].dt.date).size()
        
        if len(daily_maintenance) < 7:
            return {"error": "Need at least 7 days of maintenance data"}
        
        trend_analysis = await self.analyze_trends(
            daily_maintenance.reset_index(),
            metric_column=0,
            time_column='timestamp'
        )
        
        predicted_demand = max(0, trend_analysis.forecast_value * horizon_days)
        
        return {
            "prediction_horizon_days": horizon_days,
            "predicted_maintenance_requests": round(predicted_demand),
            "confidence": trend_analysis.confidence,
            "trend_direction": trend_analysis.direction.value,
            "resource_recommendation": self._get_resource_recommendation(predicted_demand)
        }
    
    async def _predict_cost_forecast(self, data: pd.DataFrame, horizon_days: int) -> Dict[str, Any]:
        """Predict cost forecast for the next period"""
        if data.empty:
            return {"error": "Insufficient data for prediction"}
        
        # Analyze cost trends
        daily_costs = data.groupby(data['timestamp'].dt.date)['cost_estimate'].sum()
        
        if len(daily_costs) < 7:
            return {"error": "Need at least 7 days of cost data"}
        
        trend_analysis = await self.analyze_trends(
            daily_costs.reset_index(),
            metric_column='cost_estimate',
            time_column='timestamp'
        )
        
        predicted_cost = max(0, trend_analysis.forecast_value * horizon_days)
        
        return {
            "prediction_horizon_days": horizon_days,
            "predicted_total_cost": round(predicted_cost, 2),
            "confidence": trend_analysis.confidence,
            "trend_direction": trend_analysis.direction.value,
            "budget_recommendation": self._get_budget_recommendation(predicted_cost, daily_costs.mean())
        }
    
    def _get_resource_recommendation(self, predicted_demand: float) -> str:
        """Get resource recommendation based on predicted demand"""
        if predicted_demand > 50:
            return "Consider increasing maintenance team capacity"
        elif predicted_demand > 30:
            return "Monitor resource allocation closely"
        else:
            return "Current resource levels appear adequate"
    
    def _get_budget_recommendation(self, predicted_cost: float, historical_average: float) -> str:
        """Get budget recommendation based on cost prediction"""
        if predicted_cost > historical_average * 1.5:
            return "Increase maintenance budget allocation"
        elif predicted_cost > historical_average * 1.2:
            return "Review budget allocation for potential increase"
        else:
            return "Current budget allocation appears adequate"
    
    async def _cleanup_cache(self):
        """Clean up expired cache entries"""
        current_time = datetime.utcnow()
        expired_keys = [
            key for key, value in self._cache.items()
            if current_time - value['timestamp'] > self._cache_ttl
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        self._last_cache_cleanup = current_time


# Global analytics engine instance
_analytics_engine = None


def get_analytics_engine() -> AdvancedAnalyticsEngine:
    """Get the global analytics engine instance"""
    global _analytics_engine
    if _analytics_engine is None:
        _analytics_engine = AdvancedAnalyticsEngine()
    return _analytics_engine
"""
Vessel Maintenance AI System - Database Management Module

This module handles all database operations for the vessel maintenance AI system,
including storage and retrieval of processing results, analytics data, and
system metrics. It uses SQLite for local data persistence with plans for
PostgreSQL support in production environments.

Key Features:
- Processing results storage and retrieval
- Analytics data aggregation
- Database schema management
- Query optimization for reporting
- Data backup and recovery support

Author: Fusionpact Technologies Inc.
Date: 2025-07-18
Version: 1.0.0
License: MIT License

Copyright (c) 2025 Fusionpact Technologies Inc.
Licensed under the MIT License. See LICENSE file for details.
"""

import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Import data models for type safety
from .models import ProcessingResponse, AnalyticsData

# Avoid circular imports by importing config when needed
try:
    from .config import settings
except ImportError:
    settings = None


class DatabaseManager:
    """
    Database manager for storing and retrieving vessel maintenance processing results.
    
    This class provides a comprehensive interface for database operations,
    including creation, querying, and analytics generation. It handles all
    data persistence needs for the vessel maintenance AI system.
    
    Attributes:
        db_path (str): Path to the SQLite database file
        logger (logging.Logger): Logger instance for database operations
        
    Methods:
        save_result: Store processing results
        get_results: Retrieve stored results with filtering
        get_analytics: Generate analytics data
        cleanup_old_records: Remove old records for maintenance
    """
    
    def __init__(self, db_path: str = "data/vessel_maintenance.db"):
        """
        Initialize the database manager.
        
        Sets up the database connection, creates necessary directories,
        and initializes the database schema if it doesn't exist.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._ensure_db_directory()
        self._initialize_database()
        
        # Initialize SQLAlchemy for enterprise features
        self.engine = None
        self.SessionLocal = None
        self._init_sqlalchemy()
        
    def _ensure_db_directory(self):
        """
        Ensure the database directory exists.
        
        Creates the directory structure needed for the database file
        if it doesn't already exist.
        """
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
    def _initialize_database(self):
        """
        Initialize database tables and schema.
        
        Creates all necessary tables with proper indexes for optimal
        query performance. This method is idempotent and safe to call
        multiple times.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create main processing results table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS processing_results (
                        id TEXT PRIMARY KEY,
                        summary TEXT NOT NULL,
                        details TEXT NOT NULL,
                        classification TEXT NOT NULL,
                        priority TEXT NOT NULL,
                        confidence_score REAL NOT NULL,
                        keywords TEXT,  -- JSON array of keywords
                        entities TEXT,  -- JSON object of categorized entities
                        recommended_actions TEXT,  -- JSON array of actions
                        risk_assessment TEXT NOT NULL,
                        document_type TEXT,
                        vessel_id TEXT,
                        timestamp DATETIME NOT NULL,
                        metadata TEXT  -- JSON object for additional data
                    )
                """)
                
                # Create indexes for performance optimization
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_classification 
                    ON processing_results(classification)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_priority 
                    ON processing_results(priority)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_timestamp 
                    ON processing_results(timestamp)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_vessel_id 
                    ON processing_results(vessel_id)
                """)
                
                # Create analytics summary table for performance
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS analytics_cache (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cache_key TEXT UNIQUE NOT NULL,
                        cache_data TEXT NOT NULL,  -- JSON object
                        created_at DATETIME NOT NULL,
                        expires_at DATETIME NOT NULL
                    )
                """)
                
                # Create system metrics table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS system_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_name TEXT NOT NULL,
                        metric_value REAL NOT NULL,
                        metric_unit TEXT,
                        recorded_at DATETIME NOT NULL
                    )
                """)
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            raise
    
    def _init_sqlalchemy(self):
        """Initialize SQLAlchemy engine and session factory for enterprise features"""
        try:
            # Get database URL from settings, fallback to SQLite
            if hasattr(settings, 'get_database_url'):
                database_url = settings.get_database_url()
            else:
                database_url = f"sqlite:///{self.db_path}"
            
            # Create engine with appropriate configuration
            if database_url.startswith('sqlite'):
                self.engine = create_engine(
                    database_url,
                    poolclass=StaticPool,
                    connect_args={"check_same_thread": False},
                    echo=False
                )
            else:
                pool_size = getattr(settings, 'database_pool_size', 20)
                max_overflow = getattr(settings, 'database_max_overflow', 30)
                pool_timeout = getattr(settings, 'database_pool_timeout', 30)
                
                self.engine = create_engine(
                    database_url,
                    pool_size=pool_size,
                    max_overflow=max_overflow,
                    pool_timeout=pool_timeout,
                    echo=False
                )
            
            # Create session factory
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            self.logger.info("SQLAlchemy initialized successfully")
            
        except Exception as e:
            self.logger.error(f"SQLAlchemy initialization failed: {e}")
            # Fallback to SQLite
            self.engine = create_engine(
                f"sqlite:///{self.db_path}",
                poolclass=StaticPool,
                connect_args={"check_same_thread": False},
                echo=False
            )
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a new SQLAlchemy session for enterprise features"""
        if self.SessionLocal is None:
            self._init_sqlalchemy()
        return self.SessionLocal()
    
    def save_result(self, result: ProcessingResponse) -> bool:
        """
        Save a processing result to the database.
        
        Stores the complete processing result with all associated metadata
        for later retrieval and analytics generation.
        
        Args:
            result (ProcessingResponse): The processing result to store
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Prepare data for insertion
                cursor.execute("""
                    INSERT OR REPLACE INTO processing_results (
                        id, summary, details, classification, priority, 
                        confidence_score, keywords, entities, recommended_actions,
                        risk_assessment, document_type, vessel_id, timestamp, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result.id,
                    result.summary,
                    result.details,
                    result.classification,
                    result.priority,
                    result.confidence_score,
                    json.dumps(result.keywords),  # Serialize list to JSON
                    json.dumps(result.entities),  # Serialize dict to JSON
                    json.dumps(result.recommended_actions),  # Serialize list to JSON
                    result.risk_assessment,
                    result.document_type,
                    result.vessel_id,
                    result.timestamp.isoformat(),
                    json.dumps(result.metadata)  # Serialize dict to JSON
                ))
                
                conn.commit()
                self.logger.info(f"Saved processing result: {result.id}")
                
                # Invalidate analytics cache since new data was added
                self._invalidate_analytics_cache()
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error saving result: {e}")
            return False
    
    def get_results(self, limit: int = 100, classification: str = None, 
                   priority: str = None, vessel_id: str = None, 
                   days_back: int = 30) -> List[Dict[str, Any]]:
        """
        Retrieve processing results with optional filtering.
        
        Fetches processing results from the database with support for
        various filtering criteria to support different use cases.
        
        Args:
            limit (int): Maximum number of results to return
            classification (str, optional): Filter by classification type
            priority (str, optional): Filter by priority level
            vessel_id (str, optional): Filter by vessel identifier
            days_back (int): Number of days to look back for results
            
        Returns:
            List[Dict[str, Any]]: List of processing results as dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # Enable dict-like access
                cursor = conn.cursor()
                
                # Build dynamic query based on filters
                query = """
                    SELECT * FROM processing_results 
                    WHERE timestamp >= ?
                """
                params = [datetime.now() - timedelta(days=days_back)]
                
                # Add optional filters
                if classification:
                    query += " AND classification = ?"
                    params.append(classification)
                    
                if priority:
                    query += " AND priority = ?"
                    params.append(priority)
                    
                if vessel_id:
                    query += " AND vessel_id = ?"
                    params.append(vessel_id)
                
                # Order by timestamp descending and apply limit
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # Convert rows to dictionaries and deserialize JSON fields
                results = []
                for row in rows:
                    result_dict = dict(row)
                    
                    # Deserialize JSON fields
                    try:
                        result_dict['keywords'] = json.loads(result_dict['keywords'] or '[]')
                        result_dict['entities'] = json.loads(result_dict['entities'] or '{}')
                        result_dict['recommended_actions'] = json.loads(result_dict['recommended_actions'] or '[]')
                        result_dict['metadata'] = json.loads(result_dict['metadata'] or '{}')
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"Error deserializing JSON for result {result_dict['id']}: {e}")
                        # Set defaults for corrupted data
                        result_dict['keywords'] = []
                        result_dict['entities'] = {}
                        result_dict['recommended_actions'] = []
                        result_dict['metadata'] = {}
                    
                    results.append(result_dict)
                
                self.logger.info(f"Retrieved {len(results)} results with filters")
                return results
                
        except Exception as e:
            self.logger.error(f"Error retrieving results: {e}")
            return []
    
    def get_analytics(self, days_back: int = 30) -> AnalyticsData:
        """
        Generate analytics data for the specified time period.
        
        Aggregates processing results to generate comprehensive analytics
        including classification breakdowns, priority distributions, and
        trend analysis for monitoring and reporting.
        
        Args:
            days_back (int): Number of days to include in analytics
            
        Returns:
            AnalyticsData: Comprehensive analytics data object
        """
        # Try to get cached analytics first
        cache_key = f"analytics_{days_back}d"
        cached_analytics = self._get_cached_analytics(cache_key)
        if cached_analytics:
            return cached_analytics
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cutoff_date = datetime.now() - timedelta(days=days_back)
                
                # Get total processed count
                cursor.execute("""
                    SELECT COUNT(*) FROM processing_results 
                    WHERE timestamp >= ?
                """, (cutoff_date,))
                total_processed = cursor.fetchone()[0]
                
                # Get critical alerts count
                cursor.execute("""
                    SELECT COUNT(*) FROM processing_results 
                    WHERE timestamp >= ? AND priority = 'Critical'
                """, (cutoff_date,))
                critical_alerts = cursor.fetchone()[0]
                
                # Get classification breakdown
                cursor.execute("""
                    SELECT classification, COUNT(*) as count 
                    FROM processing_results 
                    WHERE timestamp >= ?
                    GROUP BY classification
                """, (cutoff_date,))
                classification_breakdown = dict(cursor.fetchall())
                
                # Get priority breakdown
                cursor.execute("""
                    SELECT priority, COUNT(*) as count 
                    FROM processing_results 
                    WHERE timestamp >= ?
                    GROUP BY priority
                """, (cutoff_date,))
                priority_breakdown = dict(cursor.fetchall())
                
                # Get recent trends (daily counts for the last 7 days)
                recent_trends = []
                for i in range(7):
                    day_start = datetime.now() - timedelta(days=i+1)
                    day_end = datetime.now() - timedelta(days=i)
                    
                    cursor.execute("""
                        SELECT COUNT(*) FROM processing_results 
                        WHERE timestamp >= ? AND timestamp < ?
                    """, (day_start, day_end))
                    
                    count = cursor.fetchone()[0]
                    recent_trends.append({
                        "date": day_start.strftime("%Y-%m-%d"),
                        "count": count
                    })
                
                # Calculate average processing time (if metrics are available)
                average_processing_time = self._calculate_average_processing_time()
                
                # Get system performance metrics
                system_performance = self._get_system_performance_metrics()
                
                # Create analytics object
                analytics = AnalyticsData(
                    total_processed=total_processed,
                    critical_alerts=critical_alerts,
                    classification_breakdown=classification_breakdown,
                    priority_breakdown=priority_breakdown,
                    recent_trends=recent_trends,
                    average_processing_time=average_processing_time,
                    system_performance=system_performance
                )
                
                # Cache the analytics for 1 hour
                self._cache_analytics(cache_key, analytics, hours=1)
                
                self.logger.info(f"Generated analytics for {days_back} days")
                return analytics
                
        except Exception as e:
            self.logger.error(f"Error generating analytics: {e}")
            # Return empty analytics on error
            return AnalyticsData()
    
    def cleanup_old_records(self, days_to_keep: int = 90) -> int:
        """
        Remove old processing results to manage database size.
        
        Deletes processing results older than the specified number of days
        to prevent the database from growing too large over time.
        
        Args:
            days_to_keep (int): Number of days of data to retain
            
        Returns:
            int: Number of records deleted
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cutoff_date = datetime.now() - timedelta(days=days_to_keep)
                
                # Delete old processing results
                cursor.execute("""
                    DELETE FROM processing_results 
                    WHERE timestamp < ?
                """, (cutoff_date,))
                
                deleted_count = cursor.rowcount
                
                # Clean up old analytics cache entries
                cursor.execute("""
                    DELETE FROM analytics_cache 
                    WHERE expires_at < ?
                """, (datetime.now(),))
                
                # Clean up old system metrics (keep 1 year)
                metrics_cutoff = datetime.now() - timedelta(days=365)
                cursor.execute("""
                    DELETE FROM system_metrics 
                    WHERE recorded_at < ?
                """, (metrics_cutoff,))
                
                conn.commit()
                self.logger.info(f"Cleaned up {deleted_count} old records")
                return deleted_count
                
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            return 0
    
    def _invalidate_analytics_cache(self):
        """
        Invalidate all cached analytics data.
        
        Removes cached analytics to ensure fresh calculations when
        new data is added to the database.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM analytics_cache")
                conn.commit()
                
        except Exception as e:
            self.logger.warning(f"Error invalidating analytics cache: {e}")
    
    def _get_cached_analytics(self, cache_key: str) -> Optional[AnalyticsData]:
        """
        Retrieve cached analytics data if available and not expired.
        
        Args:
            cache_key (str): The cache key to look up
            
        Returns:
            Optional[AnalyticsData]: Cached analytics or None if not available
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT cache_data FROM analytics_cache 
                    WHERE cache_key = ? AND expires_at > ?
                """, (cache_key, datetime.now()))
                
                row = cursor.fetchone()
                if row:
                    cache_data = json.loads(row[0])
                    return AnalyticsData(**cache_data)
                    
        except Exception as e:
            self.logger.warning(f"Error retrieving cached analytics: {e}")
            
        return None
    
    def _cache_analytics(self, cache_key: str, analytics: AnalyticsData, hours: int = 1):
        """
        Cache analytics data for the specified duration.
        
        Args:
            cache_key (str): The cache key to store under
            analytics (AnalyticsData): The analytics data to cache
            hours (int): Number of hours to cache the data
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                expires_at = datetime.now() + timedelta(hours=hours)
                
                cursor.execute("""
                    INSERT OR REPLACE INTO analytics_cache 
                    (cache_key, cache_data, created_at, expires_at)
                    VALUES (?, ?, ?, ?)
                """, (
                    cache_key,
                    analytics.model_dump_json(),  # Serialize to JSON
                    datetime.now(),
                    expires_at
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.warning(f"Error caching analytics: {e}")
    
    def _calculate_average_processing_time(self) -> Optional[float]:
        """
        Calculate the average processing time from system metrics.
        
        Returns:
            Optional[float]: Average processing time in milliseconds, or None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT AVG(metric_value) FROM system_metrics 
                    WHERE metric_name = 'processing_time_ms' 
                    AND recorded_at >= ?
                """, (datetime.now() - timedelta(days=7),))
                
                result = cursor.fetchone()
                return result[0] if result and result[0] is not None else None
                
        except Exception as e:
            self.logger.warning(f"Error calculating average processing time: {e}")
            return None
    
    def _get_system_performance_metrics(self) -> Optional[Dict[str, Any]]:
        """
        Get recent system performance metrics.
        
        Returns:
            Optional[Dict[str, Any]]: System performance data or None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get latest CPU and memory usage
                cursor.execute("""
                    SELECT metric_name, metric_value 
                    FROM system_metrics 
                    WHERE metric_name IN ('cpu_usage_percent', 'memory_usage_percent')
                    AND recorded_at >= ?
                    ORDER BY recorded_at DESC
                    LIMIT 2
                """, (datetime.now() - timedelta(hours=1),))
                
                metrics = dict(cursor.fetchall())
                
                if metrics:
                    return {
                        "cpu_usage": metrics.get("cpu_usage_percent"),
                        "memory_usage": metrics.get("memory_usage_percent"),
                        "last_updated": datetime.now().isoformat()
                    }
                    
        except Exception as e:
            self.logger.warning(f"Error getting system performance metrics: {e}")
            
        return None
    
    def record_metric(self, metric_name: str, metric_value: float, metric_unit: str = None):
        """
        Record a system performance metric.
        
        Args:
            metric_name (str): Name of the metric being recorded
            metric_value (float): Value of the metric
            metric_unit (str, optional): Unit of measurement
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO system_metrics 
                    (metric_name, metric_value, metric_unit, recorded_at)
                    VALUES (?, ?, ?, ?)
                """, (metric_name, metric_value, metric_unit, datetime.now()))
                
                conn.commit()
                
        except Exception as e:
            self.logger.warning(f"Error recording metric {metric_name}: {e}")
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        Get database information and statistics.
        
        Returns:
            Dict[str, Any]: Database information including size, record counts, etc.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get table sizes
                cursor.execute("SELECT COUNT(*) FROM processing_results")
                results_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM analytics_cache")
                cache_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM system_metrics")
                metrics_count = cursor.fetchone()[0]
                
                # Get database file size
                db_size = Path(self.db_path).stat().st_size if Path(self.db_path).exists() else 0
                
                return {
                    "database_path": self.db_path,
                    "database_size_bytes": db_size,
                    "database_size_mb": round(db_size / 1024 / 1024, 2),
                    "processing_results_count": results_count,
                    "analytics_cache_count": cache_count,
                    "system_metrics_count": metrics_count,
                    "last_checked": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error getting database info: {e}")
            return {"error": str(e)}
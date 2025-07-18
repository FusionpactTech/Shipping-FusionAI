import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

from .models import ProcessingResponse, AnalyticsData


class DatabaseManager:
    """Database manager for storing and retrieving vessel maintenance processing results"""
    
    def __init__(self, db_path: str = "data/vessel_maintenance.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._ensure_db_directory()
        self._initialize_database()
        
    def _ensure_db_directory(self):
        """Ensure the database directory exists"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
    def _initialize_database(self):
        """Initialize database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create processing results table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS processing_results (
                        id TEXT PRIMARY KEY,
                        summary TEXT NOT NULL,
                        details TEXT NOT NULL,
                        classification TEXT NOT NULL,
                        priority TEXT NOT NULL,
                        confidence_score REAL NOT NULL,
                        keywords TEXT,  -- JSON array
                        entities TEXT,  -- JSON object
                        recommended_actions TEXT,  -- JSON array
                        risk_assessment TEXT NOT NULL,
                        document_type TEXT,
                        vessel_id TEXT,
                        timestamp TEXT NOT NULL,
                        metadata TEXT  -- JSON object
                    )
                """)
                
                # Create vessels table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS vessels (
                        vessel_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        type TEXT,
                        flag TEXT,
                        imo_number TEXT,
                        last_inspection TEXT,
                        status TEXT DEFAULT 'Active',
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """)
                
                # Create alert rules table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS alert_rules (
                        rule_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT,
                        conditions TEXT,  -- JSON array
                        classification TEXT NOT NULL,
                        priority TEXT NOT NULL,
                        actions TEXT,  -- JSON array
                        is_active BOOLEAN DEFAULT 1,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """)
                
                # Create analytics cache table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS analytics_cache (
                        cache_key TEXT PRIMARY KEY,
                        data TEXT NOT NULL,  -- JSON object
                        created_at TEXT NOT NULL,
                        expires_at TEXT NOT NULL
                    )
                """)
                
                # Create indexes for better query performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON processing_results(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_vessel_id ON processing_results(vessel_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_classification ON processing_results(classification)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_priority ON processing_results(priority)")
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            raise
    
    def store_result(self, result: ProcessingResponse) -> bool:
        """Store a processing result in the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO processing_results (
                        id, summary, details, classification, priority, confidence_score,
                        keywords, entities, recommended_actions, risk_assessment,
                        document_type, vessel_id, timestamp, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result.id,
                    result.summary,
                    result.details,
                    result.classification.value,
                    result.priority.value,
                    result.confidence_score,
                    json.dumps(result.keywords),
                    json.dumps(result.entities),
                    json.dumps(result.recommended_actions),
                    result.risk_assessment,
                    result.document_type.value if result.document_type else None,
                    result.vessel_id,
                    result.timestamp.isoformat(),
                    json.dumps(result.metadata)
                ))
                
                conn.commit()
                self.logger.info(f"Stored processing result: {result.id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error storing result: {e}")
            return False
    
    def get_history(self, limit: int = 50, vessel_id: str = None) -> List[Dict[str, Any]]:
        """Get processing history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT * FROM processing_results
                    WHERE 1=1
                """
                params = []
                
                if vessel_id:
                    query += " AND vessel_id = ?"
                    params.append(vessel_id)
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                columns = [description[0] for description in cursor.description]
                results = []
                
                for row in rows:
                    result = dict(zip(columns, row))
                    # Parse JSON fields
                    result['keywords'] = json.loads(result['keywords']) if result['keywords'] else []
                    result['entities'] = json.loads(result['entities']) if result['entities'] else {}
                    result['recommended_actions'] = json.loads(result['recommended_actions']) if result['recommended_actions'] else []
                    result['metadata'] = json.loads(result['metadata']) if result['metadata'] else {}
                    results.append(result)
                
                return results
                
        except Exception as e:
            self.logger.error(f"Error getting history: {e}")
            return []
    
    def get_analytics(self, cache_minutes: int = 30) -> AnalyticsData:
        """Get analytics data with caching"""
        cache_key = "analytics_main"
        
        try:
            # Check cache first
            cached_data = self._get_cached_analytics(cache_key, cache_minutes)
            if cached_data:
                return AnalyticsData(**cached_data)
            
            # Generate fresh analytics
            analytics = self._generate_analytics()
            
            # Cache the results
            self._cache_analytics(cache_key, analytics.dict(), cache_minutes)
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error getting analytics: {e}")
            # Return default analytics
            return AnalyticsData(
                total_processed=0,
                critical_alerts=0,
                classification_breakdown={},
                priority_breakdown={},
                recent_trends=[]
            )
    
    def _get_cached_analytics(self, cache_key: str, cache_minutes: int) -> Optional[Dict[str, Any]]:
        """Get cached analytics if still valid"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT data FROM analytics_cache
                    WHERE cache_key = ? AND expires_at > ?
                """, (cache_key, datetime.now().isoformat()))
                
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
                
        except Exception as e:
            self.logger.error(f"Error getting cached analytics: {e}")
            
        return None
    
    def _cache_analytics(self, cache_key: str, data: Dict[str, Any], cache_minutes: int):
        """Cache analytics data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                expires_at = datetime.now() + timedelta(minutes=cache_minutes)
                
                cursor.execute("""
                    INSERT OR REPLACE INTO analytics_cache (cache_key, data, created_at, expires_at)
                    VALUES (?, ?, ?, ?)
                """, (
                    cache_key,
                    json.dumps(data),
                    datetime.now().isoformat(),
                    expires_at.isoformat()
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error caching analytics: {e}")
    
    def _generate_analytics(self) -> AnalyticsData:
        """Generate fresh analytics data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total processed
                cursor.execute("SELECT COUNT(*) FROM processing_results")
                total_processed = cursor.fetchone()[0]
                
                # Critical alerts
                cursor.execute("SELECT COUNT(*) FROM processing_results WHERE priority = 'Critical'")
                critical_alerts = cursor.fetchone()[0]
                
                # Classification breakdown
                cursor.execute("""
                    SELECT classification, COUNT(*) 
                    FROM processing_results 
                    GROUP BY classification
                """)
                classification_breakdown = dict(cursor.fetchall())
                
                # Priority breakdown
                cursor.execute("""
                    SELECT priority, COUNT(*) 
                    FROM processing_results 
                    GROUP BY priority
                """)
                priority_breakdown = dict(cursor.fetchall())
                
                # Recent trends (last 7 days)
                seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
                cursor.execute("""
                    SELECT DATE(timestamp) as date, COUNT(*) as count
                    FROM processing_results 
                    WHERE timestamp >= ?
                    GROUP BY DATE(timestamp)
                    ORDER BY date
                """, (seven_days_ago,))
                
                trends_data = cursor.fetchall()
                recent_trends = [{"date": row[0], "count": row[1]} for row in trends_data]
                
                # Vessel statistics
                cursor.execute("""
                    SELECT vessel_id, COUNT(*) as count, 
                           SUM(CASE WHEN priority = 'Critical' THEN 1 ELSE 0 END) as critical_count
                    FROM processing_results 
                    WHERE vessel_id IS NOT NULL
                    GROUP BY vessel_id
                """)
                
                vessel_data = cursor.fetchall()
                vessel_stats = {}
                for row in vessel_data:
                    vessel_stats[row[0]] = {
                        "total_reports": row[1],
                        "critical_alerts": row[2]
                    }
                
                return AnalyticsData(
                    total_processed=total_processed,
                    critical_alerts=critical_alerts,
                    classification_breakdown=classification_breakdown,
                    priority_breakdown=priority_breakdown,
                    recent_trends=recent_trends,
                    vessel_stats=vessel_stats
                )
                
        except Exception as e:
            self.logger.error(f"Error generating analytics: {e}")
            raise
    
    def store_vessel(self, vessel_data: Dict[str, Any]) -> bool:
        """Store vessel information"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                now = datetime.now().isoformat()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO vessels (
                        vessel_id, name, type, flag, imo_number, 
                        last_inspection, status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    vessel_data.get('vessel_id'),
                    vessel_data.get('name'),
                    vessel_data.get('type'),
                    vessel_data.get('flag'),
                    vessel_data.get('imo_number'),
                    vessel_data.get('last_inspection'),
                    vessel_data.get('status', 'Active'),
                    now,
                    now
                ))
                
                conn.commit()
                self.logger.info(f"Stored vessel: {vessel_data.get('vessel_id')}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error storing vessel: {e}")
            return False
    
    def get_vessels(self) -> List[Dict[str, Any]]:
        """Get all vessels"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM vessels ORDER BY name")
                rows = cursor.fetchall()
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Error getting vessels: {e}")
            return []
    
    def search_results(self, query: str, classification: str = None, 
                      priority: str = None, vessel_id: str = None,
                      start_date: str = None, end_date: str = None,
                      limit: int = 100) -> List[Dict[str, Any]]:
        """Search processing results with filters"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                sql_query = """
                    SELECT * FROM processing_results
                    WHERE (summary LIKE ? OR details LIKE ? OR keywords LIKE ?)
                """
                params = [f"%{query}%", f"%{query}%", f"%{query}%"]
                
                if classification:
                    sql_query += " AND classification = ?"
                    params.append(classification)
                
                if priority:
                    sql_query += " AND priority = ?"
                    params.append(priority)
                
                if vessel_id:
                    sql_query += " AND vessel_id = ?"
                    params.append(vessel_id)
                
                if start_date:
                    sql_query += " AND timestamp >= ?"
                    params.append(start_date)
                
                if end_date:
                    sql_query += " AND timestamp <= ?"
                    params.append(end_date)
                
                sql_query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(sql_query, params)
                rows = cursor.fetchall()
                
                columns = [description[0] for description in cursor.description]
                results = []
                
                for row in rows:
                    result = dict(zip(columns, row))
                    # Parse JSON fields
                    result['keywords'] = json.loads(result['keywords']) if result['keywords'] else []
                    result['entities'] = json.loads(result['entities']) if result['entities'] else {}
                    result['recommended_actions'] = json.loads(result['recommended_actions']) if result['recommended_actions'] else []
                    result['metadata'] = json.loads(result['metadata']) if result['metadata'] else {}
                    results.append(result)
                
                return results
                
        except Exception as e:
            self.logger.error(f"Error searching results: {e}")
            return []
    
    def cleanup_old_data(self, days: int = 90):
        """Clean up old data beyond specified days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
                
                # Clean old processing results
                cursor.execute("DELETE FROM processing_results WHERE timestamp < ?", (cutoff_date,))
                deleted_results = cursor.rowcount
                
                # Clean old analytics cache
                cursor.execute("DELETE FROM analytics_cache WHERE expires_at < ?", (datetime.now().isoformat(),))
                deleted_cache = cursor.rowcount
                
                conn.commit()
                
                self.logger.info(f"Cleaned up {deleted_results} old results and {deleted_cache} cache entries")
                
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
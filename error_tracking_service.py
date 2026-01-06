"""
Error Tracking Service for DHII Mail
Provides comprehensive error tracking, storage, analytics, and reporting capabilities.
"""

import json
import logging
import os
import traceback
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from contextlib import contextmanager
import asyncio
import httpx

from error_handler import AppError, ErrorCategory, ErrorSeverity
from database import get_db

logger = logging.getLogger(__name__)

class ErrorStatus(Enum):
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    IGNORED = "ignored"

@dataclass
class ErrorContext:
    """Enhanced error context with additional metadata"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    environment: Optional[str] = None
    version: Optional[str] = None
    server_name: Optional[str] = None
    deployment_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ErrorMetrics:
    """Error metrics for analytics"""
    occurrence_count: int = 1
    first_seen: datetime = None
    last_seen: datetime = None
    affected_users: set = None
    affected_sessions: set = None
    
    def __post_init__(self):
        if self.first_seen is None:
            self.first_seen = datetime.now(timezone.utc)
        if self.last_seen is None:
            self.last_seen = datetime.now(timezone.utc)
        if self.affected_users is None:
            self.affected_users = set()
        if self.affected_sessions is None:
            self.affected_sessions = set()

class ErrorTrackingService:
    """Comprehensive error tracking service"""
    
    def __init__(self):
        self.db = get_db()
        self._ensure_error_tables()
        self.sentry_dsn = os.environ.get("SENTRY_DSN")
        self.bugsnag_api_key = os.environ.get("BUGSNAG_API_KEY")
        self.environment = os.environ.get("ENVIRONMENT", "development")
        self.version = os.environ.get("APP_VERSION", "0.1.0")
        self.deployment_id = os.environ.get("DEPLOYMENT_ID", "unknown")
        
    def _ensure_error_tables(self):
        """Create error tracking tables if they don't exist"""
        schema = """
        -- Error tracking tables
        CREATE TABLE IF NOT EXISTS error_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            error_hash VARCHAR(64) NOT NULL,
            message TEXT NOT NULL,
            category VARCHAR(50) NOT NULL,
            severity VARCHAR(20) NOT NULL,
            code VARCHAR(100),
            details JSON,
            context JSON,
            status VARCHAR(20) DEFAULT 'new',
            traceback TEXT,
            original_error_type VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS error_occurrences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            error_log_id INTEGER NOT NULL,
            user_id VARCHAR(100),
            session_id VARCHAR(100),
            request_id VARCHAR(100),
            endpoint VARCHAR(255),
            method VARCHAR(10),
            user_agent TEXT,
            ip_address VARCHAR(45),
            environment VARCHAR(50),
            version VARCHAR(50),
            server_name VARCHAR(100),
            deployment_id VARCHAR(100),
            occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (error_log_id) REFERENCES error_logs(id) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS error_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            error_log_id INTEGER NOT NULL,
            occurrence_count INTEGER DEFAULT 1,
            first_seen TIMESTAMP,
            last_seen TIMESTAMP,
            affected_users_count INTEGER DEFAULT 0,
            affected_sessions_count INTEGER DEFAULT 0,
            UNIQUE(error_log_id),
            FOREIGN KEY (error_log_id) REFERENCES error_logs(id) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS error_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            error_log_id INTEGER NOT NULL,
            alert_type VARCHAR(50) NOT NULL,
            severity VARCHAR(20) NOT NULL,
            recipient VARCHAR(255) NOT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            sent_at TIMESTAMP,
            error_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (error_log_id) REFERENCES error_logs(id) ON DELETE CASCADE
        );
        
        -- Indexes for performance
        CREATE INDEX IF NOT EXISTS idx_error_logs_error_hash ON error_logs(error_hash);
        CREATE INDEX IF NOT EXISTS idx_error_logs_category ON error_logs(category);
        CREATE INDEX IF NOT EXISTS idx_error_logs_severity ON error_logs(severity);
        CREATE INDEX IF NOT EXISTS idx_error_logs_status ON error_logs(status);
        CREATE INDEX IF NOT EXISTS idx_error_logs_created_at ON error_logs(created_at);
        CREATE INDEX IF NOT EXISTS idx_error_occurrences_error_log_id ON error_occurrences(error_log_id);
        CREATE INDEX IF NOT EXISTS idx_error_occurrences_user_id ON error_occurrences(user_id);
        CREATE INDEX IF NOT EXISTS idx_error_occurrences_occurred_at ON error_occurrences(occurred_at);
        CREATE INDEX IF NOT EXISTS idx_error_metrics_error_log_id ON error_metrics(error_log_id);
        """
        
        try:
            self.db.migrate_database(schema)
            logger.info("Error tracking tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create error tracking tables: {e}")
    
    def _generate_error_hash(self, error: AppError) -> str:
        """Generate a hash to identify similar errors"""
        import hashlib
        
        # Create a string that represents the "signature" of the error
        signature_parts = [
            error.category.value,
            error.code or "",
            str(error.message)[:100],  # First 100 chars of message
            str(error.details.get("file", ""))[:50],  # File name
            str(error.details.get("function", ""))[:30]  # Function name
        ]
        
        signature = "|".join(signature_parts)
        return hashlib.md5(signature.encode()).hexdigest()
    
    async def track_error(
        self,
        error: Union[Exception, AppError],
        context: Optional[ErrorContext] = None,
        additional_details: Optional[Dict[str, Any]] = None
    ) -> Optional[int]:
        """Track an error with comprehensive metadata"""
        
        try:
            # Convert to AppError if needed
            if not isinstance(error, AppError):
                from error_handler import ErrorHandler
                app_error = ErrorHandler.handle_error(error)
            else:
                app_error = error
            
            # Generate error hash for deduplication
            error_hash = self._generate_error_hash(app_error)
            
            # Get or create error log entry
            existing_error = self.db.execute_query(
                "SELECT id FROM error_logs WHERE error_hash = ? ORDER BY created_at DESC LIMIT 1",
                (error_hash,)
            )
            
            if existing_error:
                error_log_id = existing_error[0]['id']
                # Update existing error
                self.db.execute_update(
                    """UPDATE error_logs SET 
                       occurrence_count = occurrence_count + 1,
                       last_seen = ?,
                       updated_at = ?
                       WHERE id = ?""",
                    (datetime.now(timezone.utc), datetime.now(timezone.utc), error_log_id)
                )
            else:
                # Create new error log entry
                error_data = {
                    'error_hash': error_hash,
                    'message': app_error.message,
                    'category': app_error.category.value,
                    'severity': app_error.severity.value,
                    'code': app_error.code,
                    'details': json.dumps(app_error.details),
                    'context': json.dumps(context.to_dict() if context else {}),
                    'status': ErrorStatus.NEW.value,
                    'traceback': app_error.traceback,
                    'original_error_type': type(error).__name__
                }
                
                columns = ', '.join(error_data.keys())
                placeholders = ', '.join(['?' for _ in error_data])
                query = f"INSERT INTO error_logs ({columns}) VALUES ({placeholders})"
                
                self.db.execute_update(query, tuple(error_data.values()))
                
                # Get the inserted ID
                result = self.db.execute_query("SELECT last_insert_rowid() as id")
                error_log_id = result[0]['id'] if result else None
            
            # Track occurrence
            if error_log_id and context:
                occurrence_data = {
                    'error_log_id': error_log_id,
                    'user_id': context.user_id,
                    'session_id': context.session_id,
                    'request_id': context.request_id,
                    'endpoint': context.endpoint,
                    'method': context.method,
                    'user_agent': context.user_agent,
                    'ip_address': context.ip_address,
                    'environment': context.environment or self.environment,
                    'version': context.version or self.version,
                    'server_name': context.server_name,
                    'deployment_id': context.deployment_id or self.deployment_id
                }
                
                columns = ', '.join(occurrence_data.keys())
                placeholders = ', '.join(['?' for _ in occurrence_data])
                query = f"INSERT INTO error_occurrences ({columns}) VALUES ({placeholders})"
                
                self.db.execute_update(query, tuple(occurrence_data.values()))
            
            # Update metrics
            if error_log_id:
                self._update_error_metrics(error_log_id, context)
            
            # Send to external services
            await self._report_to_external_services(app_error, context)
            
            # Check for alerts
            await self._check_alerts(app_error, error_log_id)
            
            logger.info(f"Error tracked successfully: {app_error.code or app_error.category.value}")
            return error_log_id
            
        except Exception as e:
            logger.error(f"Failed to track error: {e}")
            return None
    
    def _update_error_metrics(self, error_log_id: int, context: Optional[ErrorContext]):
        """Update error metrics for analytics"""
        try:
            # Get current metrics
            existing_metrics = self.db.execute_query(
                "SELECT * FROM error_metrics WHERE error_log_id = ?",
                (error_log_id,)
            )
            
            if existing_metrics:
                # Update existing metrics
                metrics = existing_metrics[0]
                affected_users = set(json.loads(metrics.get('affected_users_json', '[]')))
                affected_sessions = set(json.loads(metrics.get('affected_sessions_json', '[]')))
                
                if context:
                    if context.user_id:
                        affected_users.add(context.user_id)
                    if context.session_id:
                        affected_sessions.add(context.session_id)
                
                self.db.execute_update(
                    """UPDATE error_metrics SET 
                       occurrence_count = occurrence_count + 1,
                       last_seen = ?,
                       affected_users_count = ?,
                       affected_sessions_count = ?,
                       affected_users_json = ?,
                       affected_sessions_json = ?
                       WHERE error_log_id = ?""",
                    (
                        datetime.now(timezone.utc),
                        len(affected_users),
                        len(affected_sessions),
                        json.dumps(list(affected_users)),
                        json.dumps(list(affected_sessions)),
                        error_log_id
                    )
                )
            else:
                # Create new metrics
                affected_users = set()
                affected_sessions = set()
                
                if context:
                    if context.user_id:
                        affected_users.add(context.user_id)
                    if context.session_id:
                        affected_sessions.add(context.session_id)
                
                self.db.execute_update(
                    """INSERT INTO error_metrics 
                       (error_log_id, occurrence_count, first_seen, last_seen,
                        affected_users_count, affected_sessions_count,
                        affected_users_json, affected_sessions_json)
                       VALUES (?, 1, ?, ?, ?, ?, ?, ?)""",
                    (
                        error_log_id,
                        datetime.now(timezone.utc),
                        datetime.now(timezone.utc),
                        len(affected_users),
                        len(affected_sessions),
                        json.dumps(list(affected_users)),
                        json.dumps(list(affected_sessions))
                    )
                )
                
        except Exception as e:
            logger.error(f"Failed to update error metrics: {e}")
    
    async def _report_to_external_services(self, error: AppError, context: Optional[ErrorContext]):
        """Report errors to external services like Sentry or Bugsnag"""
        
        # Report to Sentry
        if self.sentry_dsn:
            try:
                await self._report_to_sentry(error, context)
            except Exception as e:
                logger.error(f"Failed to report to Sentry: {e}")
        
        # Report to Bugsnag
        if self.bugsnag_api_key:
            try:
                await self._report_to_bugsnag(error, context)
            except Exception as e:
                logger.error(f"Failed to report to Bugsnag: {e}")
    
    async def _report_to_sentry(self, error: AppError, context: Optional[ErrorContext]):
        """Report error to Sentry"""
        try:
            import sentry_sdk
            from sentry_sdk import configure_scope
            
            # Initialize Sentry if not already done
            if not sentry_sdk.Hub.current.client:
                sentry_sdk.init(
                    dsn=self.sentry_dsn,
                    environment=self.environment,
                    release=self.version
                )
            
            with configure_scope() as scope:
                # Set user context
                if context and context.user_id:
                    scope.user = {"id": context.user_id}
                
                # Set extra context
                if context:
                    scope.set_context("request", {
                        "url": context.endpoint,
                        "method": context.method,
                        "user_agent": context.user_agent,
                        "ip_address": context.ip_address
                    })
                
                # Set tags
                scope.set_tag("error.category", error.category.value)
                scope.set_tag("error.severity", error.severity.value)
                scope.set_tag("error.code", error.code or "unknown")
                scope.set_tag("environment", self.environment)
                scope.set_tag("deployment_id", self.deployment_id)
                
                # Capture exception
                sentry_sdk.capture_exception(error.original_error or Exception(error.message))
                
        except ImportError:
            logger.warning("Sentry SDK not installed, skipping Sentry reporting")
        except Exception as e:
            logger.error(f"Failed to report to Sentry: {e}")
    
    async def _report_to_bugsnag(self, error: AppError, context: Optional[ErrorContext]):
        """Report error to Bugsnag"""
        try:
            import bugsnag
            
            # Configure Bugsnag
            bugsnag.configure(
                api_key=self.bugsnag_api_key,
                release_stage=self.environment,
                app_version=self.version
            )
            
            # Create metadata
            metadata = {
                "category": error.category.value,
                "severity": error.severity.value,
                "code": error.code or "unknown",
                "details": error.details,
                "deployment_id": self.deployment_id
            }
            
            if context:
                metadata.update({
                    "endpoint": context.endpoint,
                    "method": context.method,
                    "user_agent": context.user_agent,
                    "ip_address": context.ip_address,
                    "server_name": context.server_name
                })
            
            # Notify Bugsnag
            bugsnag.notify(
                exception=error.original_error or Exception(error.message),
                context=context.user_id if context else None,
                metadata=metadata
            )
            
        except ImportError:
            logger.warning("Bugsnag SDK not installed, skipping Bugsnag reporting")
        except Exception as e:
            logger.error(f"Failed to report to Bugsnag: {e}")
    
    async def _check_alerts(self, error: AppError, error_log_id: Optional[int]):
        """Check if alerts should be sent for this error"""
        
        # Only alert for high/critical severity errors
        if error.severity not in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            return
        
        # Check if we've already sent an alert recently
        if error_log_id:
            recent_alerts = self.db.execute_query(
                """SELECT COUNT(*) as count FROM error_alerts 
                   WHERE error_log_id = ? AND alert_type = 'email' 
                   AND created_at > datetime('now', '-1 hour')""",
                (error_log_id,)
            )
            
            if recent_alerts and recent_alerts[0]['count'] > 0:
                logger.info("Alert already sent recently, skipping")
                return
        
        # Get alert recipients from environment
        alert_recipients = os.environ.get("ERROR_ALERT_RECIPIENTS", "").split(",")
        alert_recipients = [email.strip() for email in alert_recipients if email.strip()]
        
        if not alert_recipients:
            logger.warning("No alert recipients configured")
            return
        
        # Create alert records
        for recipient in alert_recipients:
            try:
                self.db.execute_update(
                    """INSERT INTO error_alerts 
                       (error_log_id, alert_type, severity, recipient, status, error_count)
                       VALUES (?, 'email', ?, ?, 'pending', 1)""",
                    (error_log_id, error.severity.value, recipient)
                )
            except Exception as e:
                logger.error(f"Failed to create alert record: {e}")
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for the last N hours"""
        try:
            since = datetime.now(timezone.utc).timestamp() - (hours * 3600)
            
            # Get error counts by severity
            severity_counts = self.db.execute_query(
                """SELECT severity, COUNT(*) as count 
                   FROM error_logs 
                   WHERE created_at > datetime(?, 'unixepoch')
                   GROUP BY severity""",
                (since,)
            )
            
            # Get error counts by category
            category_counts = self.db.execute_query(
                """SELECT category, COUNT(*) as count 
                   FROM error_logs 
                   WHERE created_at > datetime(?, 'unixepoch')
                   GROUP BY category""",
                (since,)
            )
            
            # Get top errors
            top_errors = self.db.execute_query(
                """SELECT message, severity, COUNT(*) as count 
                   FROM error_logs 
                   WHERE created_at > datetime(?, 'unixepoch')
                   GROUP BY message, severity
                   ORDER BY count DESC
                   LIMIT 10""",
                (since,)
            )
            
            # Get total error count
            total_errors = self.db.execute_query(
                """SELECT COUNT(*) as count 
                   FROM error_logs 
                   WHERE created_at > datetime(?, 'unixepoch')""",
                (since,)
            )
            
            return {
                "hours": hours,
                "total_errors": total_errors[0]['count'] if total_errors else 0,
                "severity_breakdown": {row['severity']: row['count'] for row in severity_counts},
                "category_breakdown": {row['category']: row['count'] for row in category_counts},
                "top_errors": [
                    {
                        "message": row['message'],
                        "severity": row['severity'],
                        "count": row['count']
                    } for row in top_errors
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get error summary: {e}")
            return {}
    
    def get_error_details(self, error_log_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific error"""
        try:
            # Get error log
            error_log = self.db.execute_query(
                "SELECT * FROM error_logs WHERE id = ?",
                (error_log_id,)
            )
            
            if not error_log:
                return None
            
            error_data = error_log[0]
            
            # Get occurrences
            occurrences = self.db.execute_query(
                """SELECT * FROM error_occurrences 
                   WHERE error_log_id = ?
                   ORDER BY occurred_at DESC
                   LIMIT 100""",
                (error_log_id,)
            )
            
            # Get metrics
            metrics = self.db.execute_query(
                "SELECT * FROM error_metrics WHERE error_log_id = ?",
                (error_log_id,)
            )
            
            return {
                "error": dict(error_data),
                "occurrences": [dict(occ) for occ in occurrences],
                "metrics": dict(metrics[0]) if metrics else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get error details: {e}")
            return None
    
    def acknowledge_error(self, error_log_id: int, user_id: str) -> bool:
        """Acknowledge an error"""
        try:
            self.db.execute_update(
                """UPDATE error_logs SET 
                   status = ?, updated_at = ?
                   WHERE id = ?""",
                (ErrorStatus.ACKNOWLEDGED.value, datetime.now(timezone.utc), error_log_id)
            )
            logger.info(f"Error {error_log_id} acknowledged by user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to acknowledge error: {e}")
            return False
    
    def resolve_error(self, error_log_id: int, user_id: str, resolution_notes: str = "") -> bool:
        """Mark an error as resolved"""
        try:
            self.db.execute_update(
                """UPDATE error_logs SET 
                   status = ?, details = json_set(details, '$.resolution_notes', ?),
                   updated_at = ?
                   WHERE id = ?""",
                (ErrorStatus.RESOLVED.value, resolution_notes, datetime.now(timezone.utc), error_log_id)
            )
            logger.info(f"Error {error_log_id} resolved by user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to resolve error: {e}")
            return False


# Global error tracking service instance
_error_tracking_service = None

def get_error_tracking_service() -> ErrorTrackingService:
    """Get the global error tracking service instance"""
    global _error_tracking_service
    if _error_tracking_service is None:
        _error_tracking_service = ErrorTrackingService()
    return _error_tracking_service
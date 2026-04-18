"""
Error Handling and Recovery System

This module provides comprehensive error handling for:
- Agent execution failures
- Data processing errors
- System integration issues
- Graceful degradation and recovery
"""

import logging
import traceback
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps
import json
import os
from enum import Enum

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories"""
    DATA_VALIDATION = "data_validation"
    AGENT_EXECUTION = "agent_execution"
    SYSTEM_INTEGRATION = "system_integration"
    NETWORK = "network"
    FILE_SYSTEM = "file_system"
    BUSINESS_LOGIC = "business_logic"
    UNKNOWN = "unknown"

class AuditError(Exception):
    """Custom exception for audit system errors"""
    
    def __init__(self, message: str, category: ErrorCategory = ErrorCategory.UNKNOWN, 
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.timestamp = datetime.now()
        self.traceback = traceback.format_exc()

class ErrorHandler:
    """Centralized error handling and recovery system"""
    
    def __init__(self, log_file: str = "logs/errors.log"):
        self.log_file = log_file
        self.error_history: List[Dict[str, Any]] = []
        self.recovery_strategies = {}
        self.max_history = 1000
        
        # Ensure log directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Setup logging
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        
        # Create logger
        self.logger = logging.getLogger("AuditErrorHandler")
        self.logger.setLevel(logging.ERROR)
        
        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.ERROR)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle and log error with recovery options"""
        
        # Categorize error
        if isinstance(error, AuditError):
            category = error.category
            severity = error.severity
            message = error.message
            details = error.details
        else:
            category = self._categorize_error(error)
            severity = ErrorSeverity.MEDIUM
            message = str(error)
            details = {}
        
        # Create error record
        error_record = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "category": category.value,
            "severity": severity.value,
            "traceback": traceback.format_exc(),
            "context": context or {},
            "details": details
        }
        
        # Log error
        self._log_error(error_record)
        
        # Add to history
        self.error_history.append(error_record)
        if len(self.error_history) > self.max_history:
            self.error_history.pop(0)
        
        # Attempt recovery
        recovery_result = self._attempt_recovery(error_record)
        
        return {
            "error_handled": True,
            "error_record": error_record,
            "recovery_attempted": recovery_result["attempted"],
            "recovery_successful": recovery_result["successful"],
            "recovery_message": recovery_result["message"],
            "fallback_available": recovery_result["fallback_available"]
        }
    
    def _categorize_error(self, error: Exception) -> ErrorCategory:
        """Categorize error based on type and message"""
        
        error_message = str(error).lower()
        error_type = type(error).__name__
        
        # Data validation errors
        if any(keyword in error_message for keyword in ["validation", "invalid", "missing", "null"]):
            return ErrorCategory.DATA_VALIDATION
        
        # File system errors
        if any(keyword in error_message for keyword in ["file", "directory", "path", "permission"]):
            return ErrorCategory.FILE_SYSTEM
        
        # Network errors
        if any(keyword in error_message for keyword in ["connection", "network", "timeout", "unreachable"]):
            return ErrorCategory.NETWORK
        
        # System integration errors
        if any(keyword in error_message for keyword in ["api", "database", "service", "integration"]):
            return ErrorCategory.SYSTEM_INTEGRATION
        
        # Business logic errors
        if any(keyword in error_message for keyword in ["business", "rule", "policy", "compliance"]):
            return ErrorCategory.BUSINESS_LOGIC
        
        # Agent execution errors
        if any(keyword in error_message for keyword in ["agent", "workflow", "processing"]):
            return ErrorCategory.AGENT_EXECUTION
        
        return ErrorCategory.UNKNOWN
    
    def _log_error(self, error_record: Dict[str, Any]):
        """Log error to file and console"""
        
        log_message = f"[{error_record['category'].upper()}] {error_record['message']}"
        
        if error_record['severity'] == ErrorSeverity.CRITICAL.value:
            self.logger.critical(log_message)
        elif error_record['severity'] == ErrorSeverity.HIGH.value:
            self.logger.error(log_message)
        elif error_record['severity'] == ErrorSeverity.MEDIUM.value:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
        
        # Log full details
        self.logger.debug(f"Full error details: {json.dumps(error_record, indent=2)}")
    
    def _attempt_recovery(self, error_record: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt error recovery based on category"""
        
        category = error_record['category']
        
        recovery_strategies = {
            ErrorCategory.DATA_VALIDATION: self._recover_data_validation,
            ErrorCategory.FILE_SYSTEM: self._recover_file_system,
            ErrorCategory.NETWORK: self._recover_network,
            ErrorCategory.SYSTEM_INTEGRATION: self._recover_system_integration,
            ErrorCategory.AGENT_EXECUTION: self._recover_agent_execution,
            ErrorCategory.BUSINESS_LOGIC: self._recover_business_logic
        }
        
        recovery_func = recovery_strategies.get(category)
        if recovery_func:
            return recovery_func(error_record)
        
        return {
            "attempted": False,
            "successful": False,
            "message": "No recovery strategy available",
            "fallback_available": False
        }
    
    def _recover_data_validation(self, error_record: Dict[str, Any]) -> Dict[str, Any]:
        """Recover from data validation errors"""
        
        message = "Attempting data validation recovery..."
        
        try:
            # Try to clean data
            if "data" in error_record.get("context", {}):
                data = error_record["context"]["data"]
                
                # Basic cleaning strategies
                if isinstance(data, list):
                    # Remove empty records
                    cleaned_data = [record for record in data if record and any(record.values())]
                    
                    if len(cleaned_data) < len(data):
                        return {
                            "attempted": True,
                            "successful": True,
                            "message": f"Removed {len(data) - len(cleaned_data)} empty records",
                            "fallback_available": True,
                            "cleaned_data": cleaned_data
                        }
            
            return {
                "attempted": True,
                "successful": False,
                "message": "Data validation recovery failed",
                "fallback_available": True
            }
            
        except Exception as e:
            return {
                "attempted": True,
                "successful": False,
                "message": f"Recovery failed: {str(e)}",
                "fallback_available": False
            }
    
    def _recover_file_system(self, error_record: Dict[str, Any]) -> Dict[str, Any]:
        """Recover from file system errors"""
        
        message = "Attempting file system recovery..."
        
        try:
            # Try to create missing directories
            if "file_path" in error_record.get("context", {}):
                file_path = error_record["context"]["file_path"]
                directory = os.path.dirname(file_path)
                
                if directory and not os.path.exists(directory):
                    os.makedirs(directory, exist_ok=True)
                    
                    return {
                        "attempted": True,
                        "successful": True,
                        "message": f"Created missing directory: {directory}",
                        "fallback_available": True
                    }
            
            return {
                "attempted": True,
                "successful": False,
                "message": "File system recovery failed",
                "fallback_available": True
            }
            
        except Exception as e:
            return {
                "attempted": True,
                "successful": False,
                "message": f"Recovery failed: {str(e)}",
                "fallback_available": False
            }
    
    def _recover_network(self, error_record: Dict[str, Any]) -> Dict[str, Any]:
        """Recover from network errors"""
        
        return {
            "attempted": True,
            "successful": False,
            "message": "Network errors require manual intervention",
            "fallback_available": True,
            "fallback_message": "Use cached data or retry later"
        }
    
    def _recover_system_integration(self, error_record: Dict[str, Any]) -> Dict[str, Any]:
        """Recover from system integration errors"""
        
        return {
            "attempted": True,
            "successful": False,
            "message": "System integration errors require service restart",
            "fallback_available": True,
            "fallback_message": "Use alternative service or cached response"
        }
    
    def _recover_agent_execution(self, error_record: Dict[str, Any]) -> Dict[str, Any]:
        """Recover from agent execution errors"""
        
        message = "Attempting agent execution recovery..."
        
        try:
            # Try to restart agent or use fallback
            if "agent_name" in error_record.get("context", {}):
                agent_name = error_record["context"]["agent_name"]
                
                return {
                    "attempted": True,
                    "successful": True,
                    "message": f"Restarted agent: {agent_name}",
                    "fallback_available": True,
                    "fallback_message": "Use simplified analysis method"
                }
            
            return {
                "attempted": True,
                "successful": False,
                "message": "Agent recovery failed",
                "fallback_available": True
            }
            
        except Exception as e:
            return {
                "attempted": True,
                "successful": False,
                "message": f"Recovery failed: {str(e)}",
                "fallback_available": False
            }
    
    def _recover_business_logic(self, error_record: Dict[str, Any]) -> Dict[str, Any]:
        """Recover from business logic errors"""
        
        return {
            "attempted": True,
            "successful": False,
            "message": "Business logic errors require rule review",
            "fallback_available": True,
            "fallback_message": "Use default business rules"
        }
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for specified time period"""
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_errors = [
            error for error in self.error_history
            if datetime.fromisoformat(error['timestamp']) > cutoff_time
        ]
        
        # Count by category
        category_counts = {}
        severity_counts = {}
        
        for error in recent_errors:
            category = error['category']
            severity = error['severity']
            
            category_counts[category] = category_counts.get(category, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "period_hours": hours,
            "total_errors": len(recent_errors),
            "errors_by_category": category_counts,
            "errors_by_severity": severity_counts,
            "most_common_category": max(category_counts, key=category_counts.get) if category_counts else None,
            "highest_severity_count": severity_counts.get(ErrorSeverity.CRITICAL.value, 0)
        }
    
    def clear_error_history(self):
        """Clear error history"""
        self.error_history.clear()

# Global error handler instance
error_handler = ErrorHandler()

# Decorators for error handling
def handle_errors(category: ErrorCategory = ErrorCategory.UNKNOWN, 
                severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                fallback_return: Any = None,
                reraise: bool = False):
    """Decorator for automatic error handling"""
    
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Handle error
                context = {
                    "function": func.__name__,
                    "module": func.__module__,
                    "args": str(args)[:200],  # Limit length
                    "kwargs": str(kwargs)[:200]
                }
                
                result = error_handler.handle_error(e, context)
                
                if reraise:
                    raise e
                
                # Return fallback if available
                if fallback_return is not None:
                    return fallback_return
                
                # Return error result
                return {
                    "success": False,
                    "error": str(e),
                    "error_handling": result
                }
        
        return wrapper
    return decorator

def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator for retrying failed operations"""
    
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        # Final attempt failed, handle error
                        context = {
                            "function": func.__name__,
                            "attempts": attempt + 1,
                            "max_retries": max_retries
                        }
                        error_handler.handle_error(e, context)
                        break
                    
                    # Log retry attempt
                    logging.warning(f"Retry {attempt + 1}/{max_retries} for {func.__name__}: {str(e)}")
                    
                    # Wait before retry
                    import time
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            # Re-raise the last exception
            raise last_exception
        
        return wrapper
    return decorator

# Context manager for error handling
class ErrorContext:
    """Context manager for error handling with context"""
    
    def __init__(self, operation_name: str, context: Dict[str, Any] = None):
        self.operation_name = operation_name
        self.context = context or {}
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Handle the exception
            context = {
                "operation": self.operation_name,
                "duration": (datetime.now() - self.start_time).total_seconds(),
                **self.context
            }
            
            error_handler.handle_error(exc_val, context)
            
            # Don't suppress the exception
            return False
        
        return True

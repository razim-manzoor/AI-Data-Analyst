"""
Centralized error handling and validation module.
"""

import logging
from typing import Dict, Any, Optional, List
from enum import Enum

class ErrorSeverity(Enum):
    """Error severity levels."""
    INFO = "info"
    WARNING = "warning"  
    ERROR = "error"
    CRITICAL = "critical"

class SystemError:
    """Structured error representation."""
    
    def __init__(self, 
                 code: str, 
                 message: str, 
                 severity: ErrorSeverity = ErrorSeverity.ERROR,
                 context: Optional[Dict[str, Any]] = None):
        self.code = code
        self.message = message
        self.severity = severity
        self.context = context or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format."""
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
            "context": self.context
        }

class ErrorHandler:
    """Centralized error handling and logging."""
    
    def __init__(self):
        self.errors: List[SystemError] = []
        
    def add_error(self, error: SystemError) -> None:
        """Add an error to the collection."""
        self.errors.append(error)
        
        # Log based on severity
        if error.severity == ErrorSeverity.CRITICAL:
            logging.critical(f"{error.code}: {error.message}")
        elif error.severity == ErrorSeverity.ERROR:
            logging.error(f"{error.code}: {error.message}")
        elif error.severity == ErrorSeverity.WARNING:
            logging.warning(f"{error.code}: {error.message}")
        else:
            logging.info(f"{error.code}: {error.message}")
    
    def handle_exception(self, 
                        e: Exception, 
                        code: str = "GENERAL_ERROR",
                        context: Optional[Dict[str, Any]] = None) -> SystemError:
        """Handle and log an exception."""
        error = SystemError(
            code=code,
            message=str(e),
            severity=ErrorSeverity.ERROR,
            context=context
        )
        self.add_error(error)
        return error
    
    def get_errors(self, severity: Optional[ErrorSeverity] = None) -> List[SystemError]:
        """Get errors, optionally filtered by severity."""
        if severity:
            return [e for e in self.errors if e.severity == severity]
        return self.errors.copy()
    
    def clear_errors(self) -> None:
        """Clear all collected errors."""
        self.errors.clear()
    
    def has_errors(self, min_severity: ErrorSeverity = ErrorSeverity.ERROR) -> bool:
        """Check if there are errors of minimum severity."""
        severity_order = {
            ErrorSeverity.INFO: 0,
            ErrorSeverity.WARNING: 1,
            ErrorSeverity.ERROR: 2,
            ErrorSeverity.CRITICAL: 3
        }
        min_level = severity_order[min_severity]
        
        return any(
            severity_order[e.severity] >= min_level 
            for e in self.errors
        )
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get a summary of all errors."""
        summary = {
            "total_errors": len(self.errors),
            "by_severity": {}
        }
        
        for severity in ErrorSeverity:
            count = len([e for e in self.errors if e.severity == severity])
            summary["by_severity"][severity.value] = count
            
        return summary

# Global error handler instance
error_handler = ErrorHandler()

# Common error codes
class ErrorCodes:
    """Common error codes used throughout the system."""
    
    # Database errors
    DB_CONNECTION_FAILED = "DB_CONNECTION_FAILED"
    DB_QUERY_FAILED = "DB_QUERY_FAILED"
    DB_SCHEMA_ERROR = "DB_SCHEMA_ERROR"
    
    # Agent errors
    AGENT_INIT_FAILED = "AGENT_INIT_FAILED"
    AGENT_EXECUTION_FAILED = "AGENT_EXECUTION_FAILED"
    ROUTING_FAILED = "ROUTING_FAILED"
    
    # Workflow errors
    WORKFLOW_COMPILATION_FAILED = "WORKFLOW_COMPILATION_FAILED"
    STATE_UPDATE_FAILED = "STATE_UPDATE_FAILED"
    
    # Chart errors
    CHART_GENERATION_FAILED = "CHART_GENERATION_FAILED"
    CHART_EXECUTION_FAILED = "CHART_EXECUTION_FAILED"
    
    # System errors
    CONFIG_INVALID = "CONFIG_INVALID"
    INITIALIZATION_FAILED = "INITIALIZATION_FAILED"
    VALIDATION_FAILED = "VALIDATION_FAILED"

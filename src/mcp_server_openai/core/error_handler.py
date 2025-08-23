"""
Unified error handling system for MCP Server OpenAI.

This module provides centralized error handling, logging, and response formatting
to ensure consistent error management across all components.
"""

import logging
import traceback
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Type, Union

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class APIError(Exception):
    """Base exception for API-related errors."""
    
    def __init__(self, message: str, code: str = "API_ERROR", status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class ValidationError(APIError):
    """Exception for input validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR", 
            status_code=400,
            details={"field": field, **(details or {})}
        )


class ConfigurationError(APIError):
    """Exception for configuration-related errors."""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(
            message=message,
            code="CONFIGURATION_ERROR",
            status_code=500,
            details={"config_key": config_key} if config_key else {}
        )


class UnifiedErrorHandler:
    """Centralized error handling for all components."""
    
    def __init__(self, logger_name: str = "mcp.error_handler"):
        self.logger = logging.getLogger(logger_name)
        self._error_stats = {
            "total_errors": 0,
            "error_types": {},
            "last_error": None
        }
    
    def create_error_response(
        self, 
        error: Exception, 
        request: Optional[Request] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """Create a standardized error response."""
        
        error_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Update error statistics
        self._error_stats["total_errors"] += 1
        error_type_name = type(error).__name__
        self._error_stats["error_types"][error_type_name] = (
            self._error_stats["error_types"].get(error_type_name, 0) + 1
        )
        
        # Determine error details based on error type
        if isinstance(error, APIError):
            status_code = error.status_code
            error_data = {
                "code": error.code,
                "message": error.message,
                "details": error.details
            }
        elif isinstance(error, HTTPException):
            status_code = error.status_code
            error_data = {
                "code": "HTTP_ERROR",
                "message": str(error.detail),
                "details": {}
            }
        else:
            status_code = 500
            error_data = {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {"error_type": error_type_name}
            }
        
        # Create error context for logging
        error_context = {
            "error_id": error_id,
            "error_type": error_type_name,
            "status_code": status_code,
            **(context or {})
        }
        
        if request:
            error_context.update({
                "request_path": str(request.url),
                "request_method": request.method,
                "user_agent": request.headers.get("User-Agent"),
                "client_ip": request.client.host if request.client else None,
            })
        
        # Log the error
        self.logger.error(
            f"Error {error_id}: {error}",
            extra=error_context,
            exc_info=not isinstance(error, (APIError, HTTPException))
        )
        
        # Update last error for monitoring
        self._error_stats["last_error"] = {
            "error_id": error_id,
            "type": error_type_name,
            "message": str(error),
            "timestamp": timestamp,
            "status_code": status_code
        }
        
        # Create response
        response_data = {
            "error": {
                **error_data,
                "error_id": error_id,
                "timestamp": timestamp
            }
        }
        
        return JSONResponse(
            content=response_data,
            status_code=status_code
        )
    
    def log_error(
        self, 
        error: Exception, 
        context: Dict[str, Any],
        level: int = logging.ERROR
    ) -> None:
        """Log an error with structured context."""
        
        error_context = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            **context
        }
        
        self.logger.log(
            level,
            f"Error in {context.get('component', 'unknown')}: {error}",
            extra=error_context,
            exc_info=level >= logging.ERROR
        )
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get current error statistics."""
        return self._error_stats.copy()
    
    @staticmethod
    def handle_api_error(error: Exception, context: str = "API") -> Dict[str, Any]:
        """Standard API error response format (static method for backward compatibility)."""
        
        if isinstance(error, APIError):
            return {
                "error": {
                    "code": error.code,
                    "message": error.message,
                    "details": error.details,
                    "context": context,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
        else:
            return {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {"error_type": type(error).__name__},
                    "context": context,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }


# Global error handler instance
_global_error_handler = UnifiedErrorHandler()


def get_error_handler() -> UnifiedErrorHandler:
    """Get the global error handler instance."""
    return _global_error_handler


def create_error_response(
    error: Exception, 
    request: Optional[Request] = None,
    context: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Convenience function to create error responses."""
    return _global_error_handler.create_error_response(error, request, context)


def log_error(
    error: Exception, 
    context: Dict[str, Any],
    level: int = logging.ERROR
) -> None:
    """Convenience function to log errors."""
    _global_error_handler.log_error(error, context, level)

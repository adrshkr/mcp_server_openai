"""
Tests for the unified error handling system.
"""

import pytest
from fastapi import Request
from fastapi.responses import JSONResponse

from mcp_server_openai.core.error_handler import (
    APIError,
    ConfigurationError,
    UnifiedErrorHandler,
    ValidationError,
    create_error_response,
    get_error_handler,
)


class TestAPIError:
    """Test APIError exception class."""
    
    def test_api_error_creation(self):
        """Test APIError creation with default values."""
        error = APIError("Test error")
        
        assert error.message == "Test error"
        assert error.code == "API_ERROR"
        assert error.status_code == 500
        assert error.details == {}
    
    def test_api_error_with_custom_values(self):
        """Test APIError creation with custom values."""
        details = {"field": "test_field"}
        error = APIError(
            message="Custom error",
            code="CUSTOM_ERROR",
            status_code=400,
            details=details
        )
        
        assert error.message == "Custom error"
        assert error.code == "CUSTOM_ERROR"
        assert error.status_code == 400
        assert error.details == details


class TestValidationError:
    """Test ValidationError exception class."""
    
    def test_validation_error_creation(self):
        """Test ValidationError creation."""
        error = ValidationError("Invalid field", field="test_field")
        
        assert error.message == "Invalid field"
        assert error.code == "VALIDATION_ERROR"
        assert error.status_code == 400
        assert error.details["field"] == "test_field"


class TestConfigurationError:
    """Test ConfigurationError exception class."""
    
    def test_configuration_error_creation(self):
        """Test ConfigurationError creation."""
        error = ConfigurationError("Config missing", config_key="TEST_KEY")
        
        assert error.message == "Config missing"
        assert error.code == "CONFIGURATION_ERROR"
        assert error.status_code == 500
        assert error.details["config_key"] == "TEST_KEY"


class TestUnifiedErrorHandler:
    """Test UnifiedErrorHandler class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = UnifiedErrorHandler("test_handler")
    
    def test_create_error_response_with_api_error(self):
        """Test creating error response from APIError."""
        error = APIError("Test API error", code="TEST_ERROR", status_code=400)
        
        response = self.handler.create_error_response(error)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        
        # Check response content
        content = response.body.decode()
        assert "TEST_ERROR" in content
        assert "Test API error" in content
    
    def test_create_error_response_with_generic_exception(self):
        """Test creating error response from generic exception."""
        error = ValueError("Generic error")
        
        response = self.handler.create_error_response(error)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        
        # Check response content
        content = response.body.decode()
        assert "INTERNAL_ERROR" in content
        assert "An unexpected error occurred" in content
    
    def test_error_stats_tracking(self):
        """Test error statistics tracking."""
        # Initial stats
        stats = self.handler.get_error_stats()
        assert stats["total_errors"] == 0
        
        # Create some errors
        error1 = APIError("Error 1")
        error2 = ValueError("Error 2")
        
        self.handler.create_error_response(error1)
        self.handler.create_error_response(error2)
        
        # Check updated stats
        stats = self.handler.get_error_stats()
        assert stats["total_errors"] == 2
        assert stats["error_types"]["APIError"] == 1
        assert stats["error_types"]["ValueError"] == 1
        assert stats["last_error"] is not None
    
    def test_log_error(self):
        """Test error logging functionality."""
        error = ValueError("Test error")
        context = {"component": "test", "operation": "test_op"}
        
        # This should not raise an exception
        self.handler.log_error(error, context)
    
    @pytest.mark.asyncio
    async def test_create_error_response_with_request(self):
        """Test creating error response with request context."""
        # Mock request object
        class MockRequest:
            def __init__(self):
                self.url = "http://test.com/api/test"
                self.method = "POST"
                self.headers = {"User-Agent": "test-agent"}
                self.client = type('obj', (object,), {'host': '127.0.0.1'})()
        
        request = MockRequest()
        error = APIError("Test error with request")
        
        response = self.handler.create_error_response(error, request)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 500


class TestGlobalErrorHandler:
    """Test global error handler functions."""
    
    def test_get_error_handler(self):
        """Test getting global error handler."""
        handler = get_error_handler()
        
        assert isinstance(handler, UnifiedErrorHandler)
        
        # Should return the same instance
        handler2 = get_error_handler()
        assert handler is handler2
    
    def test_create_error_response_function(self):
        """Test global create_error_response function."""
        error = APIError("Global test error")
        
        response = create_error_response(error)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 500


class TestErrorHandlerIntegration:
    """Integration tests for error handler."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = UnifiedErrorHandler("integration_test")
    
    def test_multiple_error_types(self):
        """Test handling multiple different error types."""
        errors = [
            APIError("API error"),
            ValidationError("Validation error", field="test"),
            ConfigurationError("Config error", config_key="TEST"),
            ValueError("Generic error"),
            RuntimeError("Runtime error")
        ]
        
        responses = []
        for error in errors:
            response = self.handler.create_error_response(error)
            responses.append(response)
        
        # All should be JSONResponse instances
        assert all(isinstance(r, JSONResponse) for r in responses)
        
        # Check status codes
        assert responses[0].status_code == 500  # APIError default
        assert responses[1].status_code == 400  # ValidationError
        assert responses[2].status_code == 500  # ConfigurationError
        assert responses[3].status_code == 500  # Generic ValueError
        assert responses[4].status_code == 500  # Generic RuntimeError
        
        # Check error stats
        stats = self.handler.get_error_stats()
        assert stats["total_errors"] == 5
        assert len(stats["error_types"]) == 5
    
    def test_error_context_preservation(self):
        """Test that error context is preserved."""
        error = APIError("Context test", details={"original_data": "test"})
        context = {"request_id": "123", "user_id": "456"}
        
        response = self.handler.create_error_response(error, context=context)
        
        assert isinstance(response, JSONResponse)
        
        # Error should be logged with context (we can't easily test the log content,
        # but we can ensure it doesn't raise an exception)
        assert response.status_code == 500

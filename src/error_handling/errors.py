"""
Error handling framework for the project.

This module provides a comprehensive error handling system with:
- Custom exception classes
- Error codes and messages
- Logging capabilities
- Error recovery strategies
"""

import logging
import sys
from enum import Enum
from typing import Any, Dict, Optional, Union


class ErrorCode(Enum):
    """Standardized error codes for the application."""
    
    # Network/API errors (1000-1999)
    NETWORK_TIMEOUT = 1001
    NETWORK_CONNECTION_ERROR = 1002
    API_RATE_LIMIT = 1003
    API_AUTHENTICATION_ERROR = 1004
    API_NOT_FOUND = 1005
    API_SERVER_ERROR = 1006
    
    # Hugging Face specific errors (2000-2999)
    HF_MODEL_NOT_FOUND = 2001
    HF_REPOSITORY_ACCESS_ERROR = 2002
    HF_CONTRIBUTOR_PARSING_ERROR = 2003
    HF_README_FETCH_ERROR = 2004
    
    # GitHub specific errors (3000-3999)
    GITHUB_API_ERROR = 3001
    GITHUB_REPOSITORY_NOT_FOUND = 3002
    GITHUB_CONTRIBUTOR_FETCH_ERROR = 3003
    
    # Data validation errors (4000-4999)
    INVALID_MODEL_ID = 4001
    INVALID_INPUT_DATA = 4002
    MISSING_REQUIRED_FIELD = 4003
    DATA_TYPE_MISMATCH = 4004
    
    # Business logic errors (5000-5999)
    BUS_FACTOR_CALCULATION_ERROR = 5001
    LICENSE_SCORE_CALCULATION_ERROR = 5002
    NET_SCORE_CALCULATION_ERROR = 5003
    
    # System errors (9000-9999)
    CONFIGURATION_ERROR = 9001
    FILE_OPERATION_ERROR = 9002
    LOGGING_ERROR = 9003
    UNKNOWN_ERROR = 9999


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ProjectError(Exception):
    """
    Base exception class for all project-specific errors.
    
    Provides structured error handling with:
    - Error codes
    - Severity levels
    - Context information
    - Recovery suggestions
    """
    
    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
        recovery_suggestion: Optional[str] = None
    ):
        self.error_code = error_code
        self.severity = severity
        self.context = context or {}
        self.original_error = original_error
        self.recovery_suggestion = recovery_suggestion
        
        # Create detailed message
        full_message = self._create_detailed_message(message)
        super().__init__(full_message)
        
        # Log the error
        self._log_error()
    
    def _create_detailed_message(self, base_message: str) -> str:
        """Create a detailed error message with all context."""
        parts = [
            f"[{self.error_code.value}] {base_message}",
            f"Severity: {self.severity.value}",
        ]
        
        if self.context:
            context_str = ", ".join([f"{k}={v}" for k, v in self.context.items()])
            parts.append(f"Context: {context_str}")
        
        if self.original_error:
            parts.append(f"Original error: {str(self.original_error)}")
        
        if self.recovery_suggestion:
            parts.append(f"Suggestion: {self.recovery_suggestion}")
        
        return " | ".join(parts)
    
    def _log_error(self) -> None:
        """Log the error based on severity level."""
        logger = logging.getLogger(__name__)
        
        log_data = {
            "error_code": self.error_code.value,
            "severity": self.severity.value,
            "context": self.context,
            "original_error": str(self.original_error) if self.original_error else None
        }
        
        if self.severity == ErrorSeverity.CRITICAL:
            logger.critical(f"Critical error occurred: {self}", extra=log_data)
        elif self.severity == ErrorSeverity.HIGH:
            logger.error(f"High severity error: {self}", extra=log_data)
        elif self.severity == ErrorSeverity.MEDIUM:
            logger.warning(f"Medium severity error: {self}", extra=log_data)
        else:
            logger.info(f"Low severity error: {self}", extra=log_data)


class NetworkError(ProjectError):
    """Raised when network-related errors occur."""
    
    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if url:
            context["url"] = url
        if status_code:
            context["status_code"] = status_code
        
        kwargs["context"] = context
        super().__init__(error_code, message, **kwargs)


class HuggingFaceError(ProjectError):
    """Raised when Hugging Face API or scraping errors occur."""
    
    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        model_id: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if model_id:
            context["model_id"] = model_id
        
        kwargs["context"] = context
        super().__init__(error_code, message, **kwargs)


class ValidationError(ProjectError):
    """Raised when data validation fails."""
    
    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        field_name: Optional[str] = None,
        expected_type: Optional[str] = None,
        actual_value: Optional[Any] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if field_name:
            context["field_name"] = field_name
        if expected_type:
            context["expected_type"] = expected_type
        if actual_value is not None:
            context["actual_value"] = actual_value
        
        kwargs["context"] = context
        super().__init__(error_code, message, **kwargs)


class BusinessLogicError(ProjectError):
    """Raised when business logic errors occur."""
    
    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        operation: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if operation:
            context["operation"] = operation
        
        kwargs["context"] = context
        super().__init__(error_code, message, **kwargs)


def handle_network_error(
    error: Exception,
    url: Optional[str] = None,
    operation: str = "network request"
) -> NetworkError:
    """Convert a network error to a ProjectError."""
    
    if isinstance(error, requests.exceptions.Timeout):
        return NetworkError(
            ErrorCode.NETWORK_TIMEOUT,
            f"Timeout occurred during {operation}",
            url=url,
            severity=ErrorSeverity.MEDIUM,
            original_error=error,
            recovery_suggestion="Retry the operation with a longer timeout"
        )
    
    elif isinstance(error, requests.exceptions.ConnectionError):
        return NetworkError(
            ErrorCode.NETWORK_CONNECTION_ERROR,
            f"Connection error during {operation}",
            url=url,
            severity=ErrorSeverity.HIGH,
            original_error=error,
            recovery_suggestion="Check internet connection and retry"
        )
    
    elif isinstance(error, requests.exceptions.HTTPError):
        status_code = getattr(error.response, 'status_code', None)
        
        if status_code == 404:
            return NetworkError(
                ErrorCode.API_NOT_FOUND,
                f"Resource not found during {operation}",
                url=url,
                status_code=status_code,
                severity=ErrorSeverity.MEDIUM,
                original_error=error,
                recovery_suggestion="Verify the resource URL or ID"
            )
        
        elif status_code and 500 <= status_code < 600:
            return NetworkError(
                ErrorCode.API_SERVER_ERROR,
                f"Server error during {operation}",
                url=url,
                status_code=status_code,
                severity=ErrorSeverity.HIGH,
                original_error=error,
                recovery_suggestion="Retry later or contact API provider"
            )
        
        else:
            return NetworkError(
                ErrorCode.API_SERVER_ERROR,
                f"HTTP error during {operation}",
                url=url,
                status_code=status_code,
                severity=ErrorSeverity.MEDIUM,
                original_error=error,
                recovery_suggestion="Check the request parameters"
            )
    
    else:
        return NetworkError(
            ErrorCode.NETWORK_CONNECTION_ERROR,
            f"Unknown network error during {operation}",
            url=url,
            severity=ErrorSeverity.MEDIUM,
            original_error=error,
            recovery_suggestion="Check network connectivity"
        )


def validate_model_id(model_id: str) -> str:
    """
    Validate a Hugging Face model ID format.
    
    Args:
        model_id: The model ID to validate
        
    Returns:
        The validated model ID
        
    Raises:
        ValidationError: If the model ID is invalid
    """
    if not model_id or not isinstance(model_id, str):
        raise ValidationError(
            ErrorCode.INVALID_MODEL_ID,
            "Model ID must be a non-empty string",
            field_name="model_id",
            actual_value=model_id,
            severity=ErrorSeverity.MEDIUM,
            recovery_suggestion="Provide a valid model ID in format 'author/model-name'"
        )
    
    # Check format: should be "author/model-name"
    if '/' not in model_id:
        raise ValidationError(
            ErrorCode.INVALID_MODEL_ID,
            "Model ID must contain a forward slash (author/model-name format)",
            field_name="model_id",
            actual_value=model_id,
            severity=ErrorSeverity.MEDIUM,
            recovery_suggestion="Use format 'author/model-name'"
        )
    
    parts = model_id.split('/')
    if len(parts) != 2 or not all(part.strip() for part in parts):
        raise ValidationError(
            ErrorCode.INVALID_MODEL_ID,
            "Model ID must have exactly two non-empty parts separated by '/'",
            field_name="model_id",
            actual_value=model_id,
            severity=ErrorSeverity.MEDIUM,
            recovery_suggestion="Use format 'author/model-name'"
        )
    
    return model_id.strip()


def setup_error_logging(log_level: str = "INFO") -> None:
    """
    Set up logging configuration for error handling.
    
    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('errors.log')
        ]
    )

"""
Error Handling Framework for ML Score Calculator

A comprehensive error handling system that provides:
- Structured error management with custom exceptions
- Automatic retry mechanisms with exponential backoff
- Graceful degradation and fallback handling
- Detailed logging with severity levels
- Input validation utilities
- Error context managers for safe execution

Main Components:
- errors: Core error classes and validation
- error_handlers: Decorators and utilities for error handling
- error_config: Centralized configuration
- error_examples: Usage examples and best practices
"""

from .errors import (
    ErrorCode,
    ErrorSeverity,
    ProjectError,
    NetworkError,
    ValidationError,
    HuggingFaceError,
    BusinessLogicError,
    setup_error_logging,
    validate_model_id,
    handle_network_error,
)

from .error_handlers import (
    retry_on_error,
    graceful_fallback,
    handle_api_errors,
    safe_execute,
    ErrorHandler,
    create_error_summary,
)

from .error_config import (
    get_config,
    get_error_message,
    RETRY_CONFIG,
    DEFAULT_VALUES,
    LOGGING_CONFIG,
    VALIDATION_RULES,
)

__version__ = "1.0.0"
__author__ = "ML Score Calculator Team"

__all__ = [
    # Core error classes
    "ErrorCode",
    "ErrorSeverity", 
    "ProjectError",
    "NetworkError",
    "ValidationError",
    "HuggingFaceError",
    "BusinessLogicError",
    
    # Utilities
    "setup_error_logging",
    "validate_model_id",
    "handle_network_error",
    
    # Error handling decorators and utilities
    "retry_on_error",
    "graceful_fallback", 
    "handle_api_errors",
    "safe_execute",
    "ErrorHandler",
    "create_error_summary",
    
    # Configuration
    "get_config",
    "get_error_message",
    "RETRY_CONFIG",
    "DEFAULT_VALUES", 
    "LOGGING_CONFIG",
    "VALIDATION_RULES",
]

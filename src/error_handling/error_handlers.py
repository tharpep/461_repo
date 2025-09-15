"""
Error handling utilities and decorators.

This module provides:
- Error handling decorators
- Retry mechanisms
- Error recovery strategies
- Graceful degradation functions
"""

import functools
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

import requests

from .errors import (ErrorCode, ErrorSeverity, NetworkError, ProjectError,
                     handle_network_error)


def retry_on_error(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (
        NetworkError, requests.exceptions.RequestException
    )
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to retry a function on specific exceptions.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff_factor: Multiplier for delay after each retry
        exceptions: Tuple of exception types to retry on
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            current_delay = delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        # Last attempt failed, raise the error
                        break

                    logger = logging.getLogger(__name__)
                    logger.warning(
                        f"Attempt {attempt + 1} failed for "
                        f"{func.__name__}: {e}. "
                        f"Retrying in {current_delay} seconds..."
                    )

                    time.sleep(current_delay)
                    current_delay *= backoff_factor

            # Convert to ProjectError if it's not already
            if isinstance(last_exception, ProjectError):
                raise last_exception
            else:
                if isinstance(last_exception, Exception):
                    raise handle_network_error(last_exception)
                else:
                    raise last_exception  # type: ignore

        return wrapper
    return decorator


def graceful_fallback(
    fallback_value: Any = None,
    fallback_func: Optional[Callable[..., Any]] = None,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    log_errors: bool = True
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to provide graceful fallback when errors occur.

    Args:
        fallback_value: Static value to return on error
        fallback_func: Function to call for fallback value
        exceptions: Tuple of exception types to catch
        log_errors: Whether to log errors when fallback is used
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                if log_errors:
                    logger = logging.getLogger(__name__)
                    logger.warning(
                        f"Error in {func.__name__}: {e}. Using fallback."
                    )

                if fallback_func:
                    return fallback_func(*args, **kwargs)
                else:
                    return fallback_value

        return wrapper
    return decorator


def validate_inputs(
    **validators: Callable[[Any], None]
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to validate function inputs before execution.

    Args:
        **validators: Dictionary mapping parameter names to validation
                     functions
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Get function signature
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Validate each specified parameter
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    try:
                        validator(value)
                    except Exception as e:
                        from .errors import ValidationError
                        raise ValidationError(
                            ErrorCode.INVALID_INPUT_DATA,
                            f"Validation failed for parameter '{param_name}'",
                            field_name=param_name,
                            original_error=e,
                            severity=ErrorSeverity.MEDIUM
                        )

            return func(*args, **kwargs)

        return wrapper
    return decorator


def handle_api_errors(
    operation: str,
    model_id: Optional[str] = None,
    default_value: Any = None
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator specifically for handling API-related errors.

    Args:
        operation: Description of the operation being performed
        model_id: Optional model ID for context
        default_value: Default value to return on error
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                # Convert to NetworkError
                error = handle_network_error(e, operation=operation)
                if model_id:
                    error.context["model_id"] = model_id
                raise error
            except Exception as e:
                # Convert to BusinessLogicError
                from .errors import HuggingFaceError
                raise HuggingFaceError(
                    ErrorCode.HF_REPOSITORY_ACCESS_ERROR,
                    f"Error during {operation}",
                    model_id=model_id,
                    severity=ErrorSeverity.MEDIUM,
                    original_error=e,
                    recovery_suggestion=(
                        "Check model ID and network connectivity"
                    )
                )

        return wrapper
    return decorator


class ErrorHandler:
    """
    Context manager for handling errors with specific strategies.
    """

    def __init__(
        self,
        error_type: Type[Exception] = Exception,
        fallback_value: Any = None,
        fallback_func: Optional[Callable[..., Any]] = None,
        log_errors: bool = True
    ):
        self.error_type = error_type
        self.fallback_value = fallback_value
        self.fallback_func = fallback_func
        self.log_errors = log_errors
        self.error_occurred = False
        self.last_error: Optional[Exception] = None

    def __enter__(self) -> "ErrorHandler":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[Exception]],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any]
    ) -> bool:
        if exc_type and issubclass(exc_type, self.error_type):
            self.error_occurred = True
            self.last_error = exc_val

            if self.log_errors:
                logger = logging.getLogger(__name__)
                logger.warning(f"Error handled: {exc_val}")

            # Suppress the exception
            return True

        return False

    def get_result(self, *args: Any, **kwargs: Any) -> Any:
        """Get the fallback result if an error occurred."""
        if self.error_occurred:
            if self.fallback_func:
                return self.fallback_func(*args, **kwargs)
            else:
                return self.fallback_value
        return None


def safe_execute(
    func: Callable[..., Any],
    *args: Any,
    default_value: Any = None,
    error_handler: Optional[Callable[[Exception, Any], Any]] = None,
    **kwargs: Any
) -> Any:
    """
    Safely execute a function with error handling.

    Args:
        func: Function to execute
        *args: Arguments for the function
        default_value: Default value to return on error
        error_handler: Custom error handler function
        **kwargs: Keyword arguments for the function

    Returns:
        Function result or default_value on error
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if error_handler:
            return error_handler(e, *args, **kwargs)
        else:
            logger = logging.getLogger(__name__)
            logger.warning(f"Error in safe_execute for {func.__name__}: {e}")
            return default_value


def create_error_summary(errors: List[ProjectError]) -> Dict[str, Any]:
    """
    Create a summary of multiple errors.

    Args:
        errors: List of error objects

    Returns:
        Dictionary with error summary
    """
    if not errors:
        return {"total_errors": 0, "error_types": {}, "severity_breakdown": {}}

    error_types: Dict[str, int] = {}
    severity_breakdown: Dict[str, int] = {}

    for error in errors:
        # Count error types
        error_type = type(error).__name__
        error_types[error_type] = error_types.get(error_type, 0) + 1

        # Count severity levels
        if hasattr(error, 'severity'):
            severity = error.severity.value
            severity_breakdown[severity] = (
                severity_breakdown.get(severity, 0) + 1
            )

    return {
        "total_errors": len(errors),
        "error_types": error_types,
        "severity_breakdown": severity_breakdown,
        "most_common_error": (
            max(error_types.items(), key=lambda x: x[1])[0]
            if error_types else None
        ),
        "highest_severity": (
            max(severity_breakdown.keys())
            if severity_breakdown else None
        )
    }

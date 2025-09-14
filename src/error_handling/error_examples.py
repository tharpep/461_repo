"""
Examples demonstrating how to use the error handling framework.

This module shows various patterns and best practices for error handling
throughout the project.
"""

import logging
from typing import Any

try:
    from .error_handlers import (ErrorHandler, create_error_summary,
                                 graceful_fallback, retry_on_error,
                                 safe_execute)
    from .errors import (ErrorCode, ErrorSeverity, HuggingFaceError,
                         NetworkError, ValidationError, setup_error_logging,
                         validate_model_id)
except ImportError:
    # For direct execution - use type: ignore to suppress mypy warnings
    import os
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from error_handlers import ErrorHandler  # type: ignore
    from error_handlers import (create_error_summary, graceful_fallback,
                                retry_on_error, safe_execute)
    from errors import (ErrorCode, ErrorSeverity,  # type: ignore
                        HuggingFaceError, NetworkError, ValidationError,
                        setup_error_logging, validate_model_id)


def example_basic_error_handling() -> None:
    """Example of basic error handling patterns."""
    print("=== Basic Error Handling Examples ===")

    # 1. Input validation
    try:
        validate_model_id("invalid-model-id")
    except ValidationError as e:
        print(f"Validation error: {e}")
        print(f"Error code: {e.error_code.value}")
        print(f"Severity: {e.severity.value}")

    # 2. Network error handling
    try:
        validate_model_id("")  # This will raise ValidationError
    except ValidationError as e:
        print(f"Caught validation error: {e}")

    print()


def example_graceful_degradation() -> None:
    """Example of graceful degradation when errors occur."""
    print("=== Graceful Degradation Examples ===")

    @graceful_fallback(fallback_value=0, log_errors=True)
    def risky_operation(model_id: str) -> int:
        """Simulate a risky operation that might fail."""
        if model_id == "fail":
            raise HuggingFaceError(
                ErrorCode.HF_MODEL_NOT_FOUND,
                "Simulated failure",
                model_id=model_id
            )
        return 5  # Success case

    # Test successful case
    result1 = risky_operation("valid-model")
    print(f"Successful operation result: {result1}")

    # Test failure case with graceful fallback
    result2 = risky_operation("fail")
    print(f"Failed operation result (with fallback): {result2}")

    print()


def example_error_context_manager() -> None:
    """Example using ErrorHandler context manager."""
    print("=== Error Handler Context Manager Example ===")

    with ErrorHandler(
        error_type=HuggingFaceError,
        fallback_value=0,
        log_errors=True
    ) as handler:
        # This will succeed
        result = validate_model_id("author/model")
        print(f"Validation succeeded: {result}")

    print(f"Error occurred: {handler.error_occurred}")

    with ErrorHandler(
        error_type=ValidationError,
        fallback_value="default",
        log_errors=True
    ) as handler:
        # This will fail
        validate_model_id("invalid")

    print(f"Error occurred: {handler.error_occurred}")
    print(f"Fallback result: {handler.get_result()}")

    print()


def example_safe_execution() -> None:
    """Example of safe function execution."""
    print("=== Safe Execution Example ===")

    def risky_function(value: str) -> int:
        """Function that might raise an exception."""
        if value == "error":
            raise ValueError("Simulated error")
        return len(value)

    # Safe execution with default fallback
    result1 = safe_execute(risky_function, "hello", default_value=-1)
    print(f"Safe execution (success): {result1}")

    result2 = safe_execute(risky_function, "error", default_value=-1)
    print(f"Safe execution (failure): {result2}")

    # Safe execution with custom error handler
    def custom_handler(error: Exception, *args: Any, **kwargs: Any) -> str:
        return f"Custom handling: {type(error).__name__}"

    result3 = safe_execute(
        risky_function, "error", error_handler=custom_handler
    )
    print(f"Safe execution (custom handler): {result3}")

    print()


def example_error_summary() -> None:
    """Example of creating error summaries."""
    print("=== Error Summary Example ===")

    errors = [
        ValidationError(
            ErrorCode.INVALID_MODEL_ID,
            "Invalid model ID",
            severity=ErrorSeverity.MEDIUM
        ),
        NetworkError(
            ErrorCode.NETWORK_TIMEOUT,
            "Request timeout",
            severity=ErrorSeverity.HIGH
        ),
        HuggingFaceError(
            ErrorCode.HF_MODEL_NOT_FOUND,
            "Model not found",
            severity=ErrorSeverity.MEDIUM
        ),
        ValidationError(
            ErrorCode.INVALID_INPUT_DATA,
            "Invalid input",
            severity=ErrorSeverity.LOW
        ),
    ]

    summary = create_error_summary(errors)
    print("Error Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")

    print()


def example_retry_mechanism() -> None:
    """Example of retry mechanism."""
    print("=== Retry Mechanism Example ===")

    class AttemptCounter:
        def __init__(self) -> None:
            self.count = 0

    counter = AttemptCounter()

    @retry_on_error(max_retries=3, delay=0.1)
    def flaky_function() -> str:
        """Function that fails first few times."""
        counter.count += 1

        if counter.count < 3:
            raise NetworkError(
                ErrorCode.NETWORK_TIMEOUT,
                f"Attempt {counter.count} failed"
            )

        return f"Success on attempt {counter.count}"

    try:
        result = flaky_function()
        print(f"Retry success: {result}")
    except NetworkError as e:
        print(f"Retry failed: {e}")

    print()


def example_logging_setup() -> None:
    """Example of setting up error logging."""
    print("=== Logging Setup Example ===")

    # Set up logging
    setup_error_logging("INFO")

    logger = logging.getLogger(__name__)

    # Log different severity levels
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    print("Logging setup complete. Check 'errors.log' file.")
    print()


def run_all_examples() -> None:
    """Run all error handling examples."""
    print("🚀 Running Error Handling Framework Examples")
    print("=" * 60)

    example_basic_error_handling()
    example_graceful_degradation()
    example_error_context_manager()
    example_safe_execution()
    example_error_summary()
    example_retry_mechanism()
    example_logging_setup()

    print("✅ All examples completed!")


if __name__ == "__main__":
    run_all_examples()

# Error Handling Framework

A comprehensive error handling system for the ML Score Calculator project that provides structured error management, automatic retry mechanisms, graceful degradation, and detailed logging.

## 📁 Framework Components

### 1. Core Error System (`errors.py`)
- **Custom exception classes** with structured information
- **Standardized error codes** for consistent error identification
- **Severity levels** (LOW, MEDIUM, HIGH, CRITICAL)
- **Rich context information** and recovery suggestions
- **Automatic logging** with detailed error information

### 2. Error Handling Utilities (`error_handlers.py`)
- **Retry mechanisms** with exponential backoff
- **Graceful fallback** decorators
- **Input validation** utilities
- **Error context managers** for safe execution
- **Error summary generation** for debugging

### 3. Configuration (`error_config.py`)
- **Centralized settings** for retry policies, timeouts, and defaults
- **Error message templates** for consistent messaging
- **Recovery strategies** for different error types
- **Validation rules** for input data

### 4. Examples (`error_examples.py`)
- **Comprehensive examples** showing all framework features
- **Best practices** for error handling patterns
- **Real-world scenarios** and usage patterns

## 🚀 Quick Start

### Basic Usage

```python
from src.errors import (
    ProjectError, HuggingFaceError, ValidationError, 
    ErrorCode, ErrorSeverity, validate_model_id
)
from src.error_handlers import retry_on_error, graceful_fallback

# Input validation
try:
    model_id = validate_model_id("author/model-name")
except ValidationError as e:
    print(f"Validation failed: {e.error_code.value} - {e}")

# Retry mechanism
@retry_on_error(max_retries=3, delay=1.0)
def risky_operation():
    # This will automatically retry on network errors
    pass

# Graceful fallback
@graceful_fallback(fallback_value=0)
def might_fail():
    # Returns 0 if this function raises an exception
    pass
```

### Advanced Usage

```python
from src.error_handlers import ErrorHandler, safe_execute

# Context manager for error handling
with ErrorHandler(fallback_value=None, log_errors=True) as handler:
    risky_operation()

if handler.error_occurred:
    print(f"Operation failed, using fallback: {handler.get_result()}")

# Safe execution
result = safe_execute(
    risky_function, 
    "arg1", "arg2", 
    default_value="fallback",
    error_handler=custom_error_handler
)
```

## 🔧 Error Codes

The framework uses standardized error codes organized by category:

### Network/API Errors (1000-1999)
- `NETWORK_TIMEOUT = 1001`
- `NETWORK_CONNECTION_ERROR = 1002`
- `API_RATE_LIMIT = 1003`
- `API_AUTHENTICATION_ERROR = 1004`
- `API_NOT_FOUND = 1005`
- `API_SERVER_ERROR = 1006`

### Hugging Face Errors (2000-2999)
- `HF_MODEL_NOT_FOUND = 2001`
- `HF_REPOSITORY_ACCESS_ERROR = 2002`
- `HF_CONTRIBUTOR_PARSING_ERROR = 2003`
- `HF_README_FETCH_ERROR = 2004`

### GitHub Errors (3000-3999)
- `GITHUB_API_ERROR = 3001`
- `GITHUB_REPOSITORY_NOT_FOUND = 3002`
- `GITHUB_CONTRIBUTOR_FETCH_ERROR = 3003`

### Data Validation Errors (4000-4999)
- `INVALID_MODEL_ID = 4001`
- `INVALID_INPUT_DATA = 4002`
- `MISSING_REQUIRED_FIELD = 4003`
- `DATA_TYPE_MISMATCH = 4004`

### Business Logic Errors (5000-5999)
- `BUS_FACTOR_CALCULATION_ERROR = 5001`
- `LICENSE_SCORE_CALCULATION_ERROR = 5002`
- `NET_SCORE_CALCULATION_ERROR = 5003`

## 📊 Error Severity Levels

- **LOW**: Minor issues that don't affect core functionality
- **MEDIUM**: Issues that may impact user experience but are recoverable
- **HIGH**: Serious issues that significantly impact functionality
- **CRITICAL**: Critical failures that may cause system instability

## 🔄 Retry Strategies

### Automatic Retry
```python
@retry_on_error(
    max_retries=3,
    delay=1.0,
    backoff_factor=2.0,
    exceptions=(NetworkError, requests.exceptions.RequestException)
)
def network_operation():
    # Will retry up to 3 times with exponential backoff
    # Delay: 1s, 2s, 4s
    pass
```

### Graceful Fallback
```python
@graceful_fallback(
    fallback_value=0,
    fallback_func=alternative_calculation,
    exceptions=(ValidationError, NetworkError)
)
def primary_calculation():
    # Returns fallback_value or calls fallback_func on error
    pass
```

## 📝 Logging

The framework automatically logs errors with structured information:

```python
from src.errors import setup_error_logging

# Set up logging
setup_error_logging("INFO")

# Errors are automatically logged with:
# - Timestamp
# - Error code and message
# - Severity level
# - Context information
# - Stack trace
# - Recovery suggestions
```

## ⚙️ Configuration

Customize the framework behavior through `error_config.py`:

```python
from src.error_config import get_config, get_error_message

# Get configuration sections
retry_config = get_config("retry")
logging_config = get_config("logging")

# Get formatted error messages
message = get_error_message(
    "validation", 
    "invalid_model_id", 
    field="model_id"
)
```

## 🧪 Testing the Framework

Run the examples to see the framework in action:

```bash
cd /Users/andrew/Desktop/461_repo_fork
python3 -c "
import sys
sys.path.append('src')
from error_examples import run_all_examples
run_all_examples()
"
```

## 📋 Best Practices

### 1. Use Specific Error Types
```python
# Good: Specific error type
raise HuggingFaceError(ErrorCode.HF_MODEL_NOT_FOUND, "Model not found")

# Avoid: Generic exceptions
raise Exception("Something went wrong")
```

### 2. Provide Rich Context
```python
raise NetworkError(
    ErrorCode.NETWORK_TIMEOUT,
    "Request timed out",
    url="https://api.example.com",
    severity=ErrorSeverity.MEDIUM,
    context={"timeout": 15, "retry_count": 2}
)
```

### 3. Include Recovery Suggestions
```python
raise ValidationError(
    ErrorCode.INVALID_MODEL_ID,
    "Invalid model ID format",
    recovery_suggestion="Use format 'author/model-name'"
)
```

### 4. Use Decorators for Common Patterns
```python
@handle_api_errors(operation="fetching model data")
@retry_on_error(max_retries=2)
def fetch_model_data(model_id):
    # Automatic error handling and retry logic
    pass
```

## 🔍 Error Monitoring

The framework provides tools for monitoring and analyzing errors:

```python
from src.error_handlers import create_error_summary

errors = [error1, error2, error3]
summary = create_error_summary(errors)

print(f"Total errors: {summary['total_errors']}")
print(f"Most common: {summary['most_common_error']}")
print(f"Highest severity: {summary['highest_severity']}")
```

## 🎯 Integration Guide

To integrate the error handling framework into existing code:

1. **Import the framework components**
2. **Replace generic try/catch blocks** with specific error types
3. **Add input validation** using the validation utilities
4. **Use decorators** for common error handling patterns
5. **Set up logging** for error monitoring
6. **Configure retry policies** for network operations

## 📚 Examples

See `error_examples.py` for comprehensive examples of:
- Basic error handling patterns
- Graceful degradation strategies
- Error context managers
- Safe execution patterns
- Error summary generation
- Retry mechanisms
- Logging setup

## 🛠️ Maintenance

The framework is designed to be:
- **Extensible**: Easy to add new error types and handlers
- **Configurable**: Centralized settings for easy adjustment
- **Maintainable**: Clear separation of concerns
- **Testable**: Comprehensive examples and patterns
- **Documented**: Detailed documentation and examples

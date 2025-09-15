"""
Configuration settings for the error handling framework.

This module provides centralized configuration for:
- Error logging settings
- Retry policies
- Default values
- Error handling behavior
"""

from typing import Any, Dict

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "errors.log",
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5
}

# Retry configuration
RETRY_CONFIG = {
    "default_max_retries": 3,
    "default_delay": 1.0,
    "default_backoff_factor": 2.0,
    "max_delay": 60.0,  # Maximum delay between retries
    "timeout": 15.0  # Default timeout for requests
}

# Default fallback values
DEFAULT_VALUES = {
    "bus_factor_score": 0,
    "contributor_count": 0,
    "license_score": 0.0,
    "net_score": 0.0,
    "model_id": "",
    "error_message": "An error occurred"
}

# Error severity thresholds
SEVERITY_THRESHOLDS = {
    "log_levels": {
        "critical": "CRITICAL",
        "high": "ERROR",
        "medium": "WARNING",
        "low": "INFO"
    },
    "retry_on_severity": ["low", "medium"],
    "fallback_on_severity": ["medium", "high", "critical"]
}

# Hugging Face specific configuration
HF_CONFIG = {
    "base_url": "https://huggingface.co",
    "timeout": 15,
    "max_retries": 2,
    "user_agent": "ML-Score-Calculator/1.0"
}

# GitHub specific configuration
GITHUB_CONFIG = {
    "api_base_url": "https://api.github.com",
    "timeout": 15,
    "max_retries": 2,
    "rate_limit_delay": 1.0
}

# Validation rules
VALIDATION_RULES = {
    "model_id": {
        "required": True,
        "pattern": r"^[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+$",
        "min_length": 3,
        "max_length": 100
    },
    "contributor_count": {
        "min_value": 0,
        "max_value": 10000
    },
    "score_values": {
        "min_value": 0.0,
        "max_value": 1.0
    }
}

# Error messages
ERROR_MESSAGES = {
    "validation": {
        "invalid_model_id": "Model ID must be in format 'author/model-name'",
        "missing_field": "Required field '{field}' is missing",
        "invalid_type": "Field '{field}' must be of type {expected_type}",
        "out_of_range": "Value {value} is out of allowed range"
    },
    "network": {
        "timeout": "Request timed out after {timeout} seconds",
        "connection_error": "Failed to connect to {url}",
        "server_error": "Server returned error {status_code}",
        "rate_limit": "Rate limit exceeded, please retry later"
    },
    "huggingface": {
        "model_not_found": "Model '{model_id}' not found on Hugging Face",
        "access_denied": "Access denied to model '{model_id}'",
        "parse_error": "Failed to parse data from Hugging Face"
    },
    "business_logic": {
        "calculation_failed": "Failed to calculate {operation}",
        "insufficient_data": "Insufficient data for {operation}",
        "invalid_state": "Invalid state for {operation}"
    }
}

# Recovery strategies
RECOVERY_STRATEGIES = {
    "network_timeout": {
        "action": "retry",
        "max_attempts": 3,
        "delay": 2.0
    },
    "rate_limit": {
        "action": "wait_and_retry",
        "delay": 60.0
    },
    "model_not_found": {
        "action": "fallback",
        "fallback_value": 0
    },
    "parse_error": {
        "action": "log_and_fallback",
        "fallback_value": 0
    }
}


def get_config(section: str) -> Dict[str, Any]:
    """
    Get configuration for a specific section.

    Args:
        section: Configuration section name

    Returns:
        Dictionary with configuration values
    """
    config_map = {
        "logging": LOGGING_CONFIG,
        "retry": RETRY_CONFIG,
        "defaults": DEFAULT_VALUES,
        "severity": SEVERITY_THRESHOLDS,
        "huggingface": HF_CONFIG,
        "github": GITHUB_CONFIG,
        "validation": VALIDATION_RULES,
        "messages": ERROR_MESSAGES,
        "recovery": RECOVERY_STRATEGIES
    }

    return config_map.get(section, {})  # type: ignore


def get_error_message(category: str, key: str, **kwargs: Any) -> str:
    """
    Get a formatted error message.

    Args:
        category: Error message category
        key: Error message key
        **kwargs: Format parameters

    Returns:
        Formatted error message
    """
    messages = ERROR_MESSAGES.get(category, {})
    template = messages.get(key, "Unknown error")

    try:
        return template.format(**kwargs)
    except KeyError as e:
        return f"Error formatting message: missing parameter {e}"


def get_recovery_strategy(error_type: str) -> Dict[str, Any]:
    """
    Get recovery strategy for a specific error type.

    Args:
        error_type: Type of error

    Returns:
        Recovery strategy configuration
    """
    return RECOVERY_STRATEGIES.get(error_type, {
        "action": "log_and_fallback",
        "fallback_value": None
    })

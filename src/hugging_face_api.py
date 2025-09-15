import time
from typing import Any, Dict, Optional

import requests

from .logging_config import get_logger, log_error_with_context, log_performance

HF_API_BASE = "https://huggingface.co/api"

# Initialize logger for this module
logger = get_logger(__name__)


"""
Fetch model information from Hugging Face API.
Returns model metadata as dictionary.
"""


def get_model_info(model_id: str) -> tuple[Optional[Dict[str, Any]], float]:
    start_time = time.time()

    logger.debug(f"Fetching model info for: {model_id}")

    if not model_id or not model_id.strip():
        logger.warning("Empty or invalid model_id provided")
        end_time = time.time()
        log_performance("get_model_info (empty input)",
                        end_time - start_time, logger)
        return (None, end_time - start_time)

    api_url = f"{HF_API_BASE}/models/{model_id.strip()}"
    logger.debug(f"API URL: {api_url}")

    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        end_time = time.time()

        logger.info(f"Successfully fetched model info for {model_id}")
        log_performance("get_model_info", end_time - start_time, logger)
        return (response.json(), end_time - start_time)

    except Exception as e:
        end_time = time.time()
        log_error_with_context(e, f"Failed to fetch model info for {model_id}",
                               logger)
        return (None, end_time - start_time)


if __name__ == "__main__":
    model_info, exec_time = get_model_info("microsoft/DialoGPT-medium")
    if model_info:
        print(f"Model ID: {model_info.get('id', 'Unknown')}")
        print(f"Execution time: {exec_time:.3f}s")
    else:
        print(f"Failed to fetch model info (took {exec_time:.3f}s)")
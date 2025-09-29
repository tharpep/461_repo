import os
import re
import time
from typing import Tuple

from license_sub_score import fetch_readme


def detect_dataset_links(readme_text: str) -> bool:
    """
    Detect if README contains dataset links or references.
    Looks for common dataset hosting platforms and file extensions.
    """
    if not readme_text:
        return False

    # Common dataset hosting platforms and patterns
    dataset_patterns = [
        r'https?://[^\s]*\.(csv|json|jsonl|parquet|tsv|txt|zip|tar\.gz|'
        r'tar\.bz2)',
        r'https?://[^\s]*(dataset|data)[^\s]*',
        r'https?://[^\s]*(kaggle|huggingface\.co/datasets|zenodo|figshare|'
        r'drive\.google\.com)',
        r'\[.*\]\([^)]*\.(csv|json|jsonl|parquet|tsv|txt|zip|tar\.gz|'
        r'tar\.bz2)',
        r'##?\s*Dataset',
        r'##?\s*Data',
        r'dataset[:\s]',
        r'training\s+data',
        r'test\s+data',
        r'validation\s+data',
    ]

    readme_lower = readme_text.lower()

    for pattern in dataset_patterns:
        if re.search(pattern, readme_lower, re.IGNORECASE):
            return True

    return False


def detect_code_examples(readme_text: str) -> bool:
    """
    Detect if README contains code examples or script references.
    Looks for code blocks, script files, and usage examples.
    """
    if not readme_text:
        return False

    # Patterns for code examples and scripts
    code_patterns = [
        r'```[a-zA-Z]*\n.*\n```',  # Code blocks
        r'```[a-zA-Z]*\n.*',       # Incomplete code blocks
        r'\.py\b',                  # Python files
        r'\.js\b',                  # JavaScript files
        r'\.java\b',                # Java files
        r'\.cpp\b',                 # C++ files
        r'\.c\b',                   # C files
        r'\.sh\b',                  # Shell scripts
        r'\.ipynb\b',               # Jupyter notebooks
        r'##?\s*Usage',
        r'##?\s*Example',
        r'##?\s*Code',
        r'##?\s*Installation',
        r'##?\s*Quick\s+start',
        r'pip\s+install',
        r'python\s+',
        r'import\s+',
        r'from\s+',
        r'def\s+',
        r'class\s+',
        r'function\s*\(',
        r'<code>',
        r'<pre>',
    ]

    readme_lower = readme_text.lower()

    for pattern in code_patterns:
        if re.search(pattern, readme_lower, re.IGNORECASE | re.MULTILINE):
            return True

    return False


def available_dataset_code_score(model_id: str, code_link: str = "",
                                 dataset_link: str = "") -> Tuple[
                                     float, float]:
    """
    Calculate Available Dataset and Code Score.

    Uses external links when provided (full score), falls back to README
    analysis with penalty.
    Args:
        model_id: Hugging Face model ID (e.g., "tencent/SRPO")
        code_link: External GitHub/code repository link (optional)
        dataset_link: External dataset link (optional)

    Returns:
        Tuple of (score, execution_time)
    """
    start_time = time.time()

    if not model_id or not model_id.strip():
        end_time = time.time()
        return (0.0, end_time - start_time)

    # Check external links first (full score if provided)
    has_external_code = bool(code_link and code_link.strip())
    has_external_dataset = bool(dataset_link and dataset_link.strip())
    if has_external_code and has_external_dataset:
        # Both external links provided - full score
        end_time = time.time()
        return (1.0, end_time - start_time)
    elif has_external_code or has_external_dataset:
        # One external link provided - good score
        end_time = time.time()
        return (0.5, end_time - start_time)

    # No external links - fall back to README analysis with penalty
    readme_text = fetch_readme(model_id.strip())

    if not readme_text:
        end_time = time.time()
        if int(os.getenv("LOG_LEVEL", "0")) > 0:
            print(f"[ERROR] Failed to fetch README for model: {model_id}")
        return (0.0, end_time - start_time)

    # Detect dataset links and code examples in README
    has_dataset = detect_dataset_links(readme_text)
    has_code = detect_code_examples(readme_text)

    # Apply severe penalty for not having external links
    if has_dataset and has_code:
        score = 0.1  # Severe penalty: was 1.0, now 0.1
    elif has_dataset or has_code:
        score = 0.05  # Severe penalty: was 0.5, now 0.05
    else:
        score = 0.0

    end_time = time.time()
    execution_time = end_time - start_time

    if int(os.getenv("LOG_LEVEL", "0")) > 0:
        print(f"[INFO] External links: code={has_external_code}, "
              f"dataset={has_external_dataset}")
        print(f"[INFO] README analysis: dataset={has_dataset}, "
              f"code={has_code}, Score: {score}")

    return (score, execution_time)


if __name__ == "__main__":
    # Test with the example model
    model_id = "tencent/SRPO"
    score, exec_time = available_dataset_code_score(model_id)
    print(f"Model: {model_id}")
    print(f"Available Dataset and Code Score: {score}")
    print(f"Execution time: {exec_time:.3f}s")

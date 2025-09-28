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


def available_dataset_code_score(model_id: str) -> Tuple[float, float]:
    """
    Calculate Available Dataset and Code Score:
    - 0 if neither dataset links nor code examples are present
    - 0.5 if only one is present (dataset OR code)
    - 1 if both are present (dataset AND code)

    Args:
        model_id: Hugging Face model ID (e.g., "tencent/SRPO")

    Returns:
        Tuple of (score, execution_time)
    """
    start_time = time.time()

    if not model_id or not model_id.strip():
        end_time = time.time()
        return (0.0, end_time - start_time)

    # Fetch README content
    readme_text = fetch_readme(model_id.strip())

    if not readme_text:
        end_time = time.time()
        if int(os.getenv("LOG_LEVEL", "0")) > 0:
            print(f"[ERROR] Failed to fetch README for model: {model_id}")
        return (0.0, end_time - start_time)

    # Detect dataset links and code examples
    has_dataset = detect_dataset_links(readme_text)
    has_code = detect_code_examples(readme_text)

    # Calculate score based on presence
    if has_dataset and has_code:
        score = 1.0
    elif has_dataset or has_code:
        score = 0.5
    else:
        score = 0.0

    end_time = time.time()
    execution_time = end_time - start_time

    if int(os.getenv("LOG_LEVEL", "0")) > 0:
        print(f"[INFO] Dataset detected: {has_dataset}, "
              f"Code detected: {has_code}, Score: {score}")

    return (score, execution_time)


if __name__ == "__main__":
    # Test with the example model
    model_id = "tencent/SRPO"
    score, exec_time = available_dataset_code_score(model_id)
    print(f"Model: {model_id}")
    print(f"Available Dataset and Code Score: {score}")
    print(f"Execution time: {exec_time:.3f}s")

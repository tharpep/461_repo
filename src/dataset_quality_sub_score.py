import re
import time
from typing import Optional, Tuple

from src.license_sub_score import fetch_readme


def check_dataset_links(readme_text: Optional[str]) -> bool:
    """
    Check if README contains dataset links.
    Looks for common dataset hosting patterns and URLs.
    
    Args:
        readme_text: The README content as string
        
    Returns:
        bool: True if dataset links are found, False otherwise
    """
    if not readme_text:
        return False
    
    # Common dataset hosting patterns
    dataset_patterns = [
        r'https?://[^\s]+\.csv',
        r'https?://[^\s]+\.json',
        r'https?://[^\s]+\.jsonl',
        r'https?://[^\s]+\.parquet',
        r'https?://[^\s]+\.tsv',
        r'https?://[^\s]+\.txt',
        r'https?://[^\s]*dataset[^\s]*',
        r'https?://[^\s]*data[^\s]*',
        r'https?://huggingface\.co/datasets/[^\s]+',
        r'https?://[^\s]*kaggle[^\s]*',
        r'https?://[^\s]*drive\.google[^\s]*',
        r'https?://[^\s]*dropbox[^\s]*',
        r'https?://[^\s]*github[^\s]*/.*\.csv',
        r'https?://[^\s]*github[^\s]*/.*\.json',
    ]
    
    for pattern in dataset_patterns:
        if re.search(pattern, readme_text, re.IGNORECASE):
            return True
    
    return False


def check_example_scripts(readme_text: Optional[str]) -> bool:
    """
    Check if README contains example scripts or code snippets.
    
    Args:
        readme_text: The README content as string
        
    Returns:
        bool: True if example scripts are found, False otherwise
    """
    if not readme_text:
        return False
    
    # Look for code blocks
    if '```' in readme_text:
        return True
    
    # Look for example keywords
    example_keywords = [
        'example', 'usage', 'demo', 'tutorial', 'how to use',
        'quick start', 'getting started', 'sample code'
    ]
    
    readme_lower = readme_text.lower()
    for keyword in example_keywords:
        if keyword in readme_lower:
            return True
    
    return False


def evaluate_dataset_documentation(readme_text: Optional[str]) -> float:
    """
    Evaluate dataset documentation quality based on README content.
    
    Args:
        readme_text: The README content as string
        
    Returns:
        float: Score between 0.0 and 1.0 for documentation quality
    """
    if not readme_text:
        return 0.0
    
    score = 0.0
    readme_lower = readme_text.lower()
    
    # Check for dataset description (0.2 points)
    if any(keyword in readme_lower for keyword in ['dataset', 'data', 'training data']):
        score += 0.2
    
    # Check for size information (0.2 points)
    size_patterns = [
        r'\d+\s*(gb|mb|kb|tb)',
        r'\d+\s*(gigabytes?|megabytes?|kilobytes?|terabytes?)',
        r'\d+\s*rows?',
        r'\d+\s*samples?',
        r'\d+\s*examples?',
        r'size[:\s]+\d+',
        r'contains?\s+\d+'
    ]
    
    for pattern in size_patterns:
        if re.search(pattern, readme_text, re.IGNORECASE):
            score += 0.2
            break
    
    # Check for format information (0.2 points)
    format_keywords = ['csv', 'json', 'jsonl', 'parquet', 'tsv', 'txt', 'format', 'structure']
    if any(keyword in readme_lower for keyword in format_keywords):
        score += 0.2
    
    # Check for column/field descriptions (0.2 points)
    if any(keyword in readme_lower for keyword in ['column', 'field', 'attribute', 'feature', 'schema']):
        score += 0.2
    
    # Check for usage instructions (0.2 points)
    usage_keywords = ['usage', 'how to', 'load', 'download', 'access', 'install']
    if any(keyword in readme_lower for keyword in usage_keywords):
        score += 0.2
    
    return min(1.0, score)


def evaluate_license_clarity(readme_text: Optional[str]) -> float:
    """
    Evaluate license clarity for the dataset.
    
    Args:
        readme_text: The README content as string
        
    Returns:
        float: Score between 0.0 and 1.0 for license clarity
    """
    if not readme_text:
        return 0.0
    
    score = 0.0
    readme_lower = readme_text.lower()
    
    # Check for explicit license mention (0.5 points)
    license_keywords = ['license', 'licence', 'terms', 'agreement', 'permission']
    if any(keyword in readme_lower for keyword in license_keywords):
        score += 0.5
    
    # Check for specific license types (0.3 points)
    specific_licenses = [
        'mit', 'apache', 'gpl', 'lgpl', 'bsd', 'cc0', 'cc-by', 'public domain',
        'open source', 'free to use', 'commercial use', 'academic use'
    ]
    
    for license_type in specific_licenses:
        if license_type in readme_lower:
            score += 0.3
            break
    
    # Check for usage restrictions (0.2 points)
    restriction_keywords = ['restriction', 'limitation', 'prohibited', 'not allowed', 'forbidden']
    if any(keyword in readme_lower for keyword in restriction_keywords):
        score += 0.2
    
    return min(1.0, score)


def evaluate_safety_privacy(readme_text: Optional[str]) -> float:
    """
    Evaluate safety and privacy considerations mentioned in the dataset.
    
    Args:
        readme_text: The README content as string
        
    Returns:
        float: Score between 0.0 and 1.0 for safety/privacy considerations
    """
    if not readme_text:
        return 0.0
    
    score = 0.0
    readme_lower = readme_text.lower()
    
    # Check for privacy considerations (0.4 points)
    privacy_keywords = [
        'privacy', 'personal', 'pii', 'anonymized', 'anonymised', 'de-identified',
        'confidential', 'sensitive', 'data protection', 'gdpr', 'ccpa'
    ]
    
    if any(keyword in readme_lower for keyword in privacy_keywords):
        score += 0.4
    
    # Check for safety considerations (0.3 points)
    safety_keywords = [
        'safety', 'bias', 'fairness', 'ethical', 'responsible', 'harmful',
        'content warning', 'disclaimer', 'risks', 'limitations'
    ]
    
    if any(keyword in readme_lower for keyword in safety_keywords):
        score += 0.3
    
    # Check for data source information (0.3 points)
    source_keywords = ['source', 'origin', 'collected', 'gathered', 'obtained', 'derived']
    if any(keyword in readme_lower for keyword in source_keywords):
        score += 0.3
    
    return min(1.0, score)


def evaluate_curation_quality(readme_text: Optional[str]) -> float:
    """
    Evaluate curation and quality control measures mentioned.
    
    Args:
        readme_text: The README content as string
        
    Returns:
        float: Score between 0.0 and 1.0 for curation quality
    """
    if not readme_text:
        return 0.0
    
    score = 0.0
    readme_lower = readme_text.lower()
    
    # Check for quality control measures (0.4 points)
    quality_keywords = [
        'quality', 'curated', 'verified', 'validated', 'checked', 'reviewed',
        'filtered', 'cleaned', 'processed', 'preprocessed'
    ]
    
    if any(keyword in readme_lower for keyword in quality_keywords):
        score += 0.4
    
    # Check for version information (0.3 points)
    version_keywords = ['version', 'v1', 'v2', 'update', 'changelog', 'release']
    if any(keyword in readme_lower for keyword in version_keywords):
        score += 0.3
    
    # Check for statistics or metrics (0.3 points)
    stats_keywords = ['accuracy', 'precision', 'recall', 'f1', 'bleu', 'rouge', 'metric', 'statistic']
    if any(keyword in readme_lower for keyword in stats_keywords):
        score += 0.3
    
    return min(1.0, score)


def evaluate_reproducibility(readme_text: Optional[str]) -> float:
    """
    Evaluate reproducibility aspects of the dataset.
    
    Args:
        readme_text: The README content as string
        
    Returns:
        float: Score between 0.0 and 1.0 for reproducibility
    """
    if not readme_text:
        return 0.0
    
    score = 0.0
    readme_lower = readme_text.lower()
    
    # Check for code availability (0.3 points)
    code_keywords = ['code', 'github', 'repository', 'script', 'notebook', 'jupyter']
    if any(keyword in readme_lower for keyword in code_keywords):
        score += 0.3
    
    # Check for environment setup (0.3 points)
    env_keywords = ['environment', 'requirements', 'dependencies', 'install', 'setup', 'docker']
    if any(keyword in readme_lower for keyword in env_keywords):
        score += 0.3
    
    # Check for reproducibility instructions (0.4 points)
    repro_keywords = [
        'reproduce', 'reproducibility', 'replicate', 'replication', 'recreate',
        'step by step', 'instructions', 'tutorial', 'guide'
    ]
    
    if any(keyword in readme_lower for keyword in repro_keywords):
        score += 0.4
    
    return min(1.0, score)


def dataset_quality_sub_score(model_id: str) -> Tuple[float, float]:
    """
    Calculate dataset quality sub-score based on README analysis.
    
    Evaluates:
    - Available dataset and code (0.2 weight)
    - Dataset documentation quality (0.2 weight)
    - License clarity (0.2 weight)
    - Safety/privacy considerations (0.2 weight)
    - Curation/quality control (0.1 weight)
    - Reproducibility (0.1 weight)
    
    Args:
        model_id: The Hugging Face model ID
        
    Returns:
        Tuple[float, float]: (score, elapsed_time) where score is between 0.0 and 1.0
    """
    start_time = time.time()
    
    # Fetch README
    readme = fetch_readme(model_id)
    if not readme:
        end_time = time.time()
        return (0.0, end_time - start_time)
    
    # Calculate individual scores
    available_score = 0.0
    if check_dataset_links(readme):
        available_score += 0.5
    if check_example_scripts(readme):
        available_score += 0.5
    
    doc_score = evaluate_dataset_documentation(readme)
    license_score = evaluate_license_clarity(readme)
    safety_score = evaluate_safety_privacy(readme)
    curation_score = evaluate_curation_quality(readme)
    repro_score = evaluate_reproducibility(readme)
    
    # Weighted combination
    final_score = (
        available_score * 0.2 +
        doc_score * 0.2 +
        license_score * 0.2 +
        safety_score * 0.2 +
        curation_score * 0.1 +
        repro_score * 0.1
    )
    
    end_time = time.time()
    return (final_score, end_time - start_time)


if __name__ == "__main__":
    # Test with a sample model
    model_id = "google/gemma-2b"
    score, elapsed = dataset_quality_sub_score(model_id)
    print(f"Dataset quality score: {score:.3f} (elapsed: {elapsed:.3f}s)")

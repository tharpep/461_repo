import re
import time
from typing import Optional, Tuple

from src.license_sub_score import fetch_readme


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
    
    # Check for dataset description (0.2 points) - more specific with word boundaries
    dataset_patterns = [
        r'\bdataset\b', r'\btraining data\b', r'\btraining set\b', 
        r'\bdata set\b', r'\bcorpus\b', r'\bcollection\b', r'\bspecification\b'
    ]
    
    for pattern in dataset_patterns:
        if re.search(pattern, readme_lower):
            score += 0.2
            break
    
    # Check for size information (0.2 points) - enhanced patterns
    size_patterns = [
        r'\d+\s*(gb|mb|kb|tb)',
        r'\d+\s*(gigabytes?|megabytes?|kilobytes?|terabytes?)',
        r'\d+\s*rows?',
        r'\d+\s*samples?',
        r'\d+\s*examples?',
        r'\d+\s*instances?',
        r'\d+\s*records?',
        r'size[:\s]+\d+',
        r'contains?\s+\d+'
    ]
    
    for pattern in size_patterns:
        if re.search(pattern, readme_text, re.IGNORECASE):
            score += 0.2
            break
    
    # Check for format information (0.2 points) - more comprehensive
    format_keywords = [
        'csv', 'json', 'jsonl', 'parquet', 'tsv', 'txt', 'hdf5', 'feather',
        'format', 'structure', 'file format', 'data format'
    ]
    if any(keyword in readme_lower for keyword in format_keywords):
        score += 0.2
    
    # Check for column/field descriptions (0.2 points) - with word boundaries
    schema_patterns = [
        r'\bcolumn\b', r'\bfield\b', r'\battribute\b', r'\bfeature\b', 
        r'\bschema\b', r'\bmetadata\b', r'\bannotation\b', r'\blabel\b'
    ]
    
    for pattern in schema_patterns:
        if re.search(pattern, readme_lower):
            score += 0.2
            break
    
    # Check for usage instructions (0.2 points) - more comprehensive
    usage_keywords = [
        'usage', 'how to', 'load', 'download', 'access', 'install',
        'tutorial', 'guide', 'example', 'quickstart', 'getting started'
    ]
    if any(keyword in readme_lower for keyword in usage_keywords):
        score += 0.2
    
    return min(1.0, score)


def evaluate_license_clarity(readme_text: Optional[str]) -> float:
    """
    Evaluate license clarity for the dataset (different from license compatibility).
    
    Args:
        readme_text: The README content as string
        
    Returns:
        float: Score between 0.0 and 1.0 for license clarity
    """
    if not readme_text:
        return 0.0
    
    score = 0.0
    readme_lower = readme_text.lower()
    
    # Check for explicit license mention (0.5 points) - more comprehensive
    license_keywords = [
        'license', 'licence', 'terms', 'agreement', 'permission',
        'copyright', 'legal', 'rights', 'usage rights'
    ]
    if any(keyword in readme_lower for keyword in license_keywords):
        score += 0.5
    
    # Check for specific license types (0.3 points) - more comprehensive
    specific_licenses = [
        'mit', 'apache', 'gpl', 'lgpl', 'bsd', 'cc0', 'cc-by', 'public domain',
        'open source', 'free to use', 'commercial use', 'academic use',
        'creative commons', 'attribution', 'redistribution'
    ]
    
    for license_type in specific_licenses:
        if license_type in readme_lower:
            score += 0.3
            break
    
    # Check for usage restrictions (0.2 points) - more comprehensive
    restriction_keywords = [
        'restriction', 'limitation', 'prohibited', 'not allowed', 'forbidden',
        'cannot', 'must not', 'restricted use'
    ]
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
    
    # Check for privacy considerations (0.4 points) - more comprehensive
    privacy_keywords = [
        'privacy', 'personal', 'pii', 'anonymized', 'anonymised', 'de-identified',
        'confidential', 'sensitive', 'data protection', 'gdpr', 'ccpa',
        'personal information', 'private data', 'data privacy'
    ]
    
    if any(keyword in readme_lower for keyword in privacy_keywords):
        score += 0.4
    
    # Check for safety considerations (0.3 points) - more comprehensive
    safety_keywords = [
        'safety', 'bias', 'fairness', 'ethical', 'responsible', 'harmful',
        'content warning', 'disclaimer', 'risks', 'limitations',
        'toxicity', 'hate speech', 'inappropriate', 'offensive content',
        'safety guidelines', 'ethical considerations'
    ]
    
    if any(keyword in readme_lower for keyword in safety_keywords):
        score += 0.3
    
    # Check for data source information (0.3 points) - more comprehensive
    source_keywords = [
        'source', 'origin', 'collected', 'gathered', 'obtained', 'derived',
        'data source', 'origin of data', 'data collection', 'data gathering'
    ]
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
    
    # Check for quality control measures (0.4 points) - with word boundaries
    quality_patterns = [
        r'\bquality\b', r'\bcurated\b', r'\bverified\b', r'\bvalidated\b', 
        r'\bchecked\b', r'\breviewed\b', r'\bfiltered\b', r'\bcleaned\b', 
        r'\bprocessed\b', r'\bpreprocessed\b', r'\bstandardized\b', r'\bnormalized\b'
    ]
    
    for pattern in quality_patterns:
        if re.search(pattern, readme_lower):
            score += 0.4
            break
    
    # Check for version information (0.3 points) - more comprehensive
    version_keywords = [
        'version', 'v1', 'v2', 'v3', 'update', 'changelog', 'release',
        'revision', 'iteration', 'edition', 'dataset version'
    ]
    if any(keyword in readme_lower for keyword in version_keywords):
        score += 0.3
    
    # Check for statistics or metrics (0.3 points) - more comprehensive
    stats_keywords = [
        'accuracy', 'precision', 'recall', 'f1', 'bleu', 'rouge', 
        'metric', 'statistic', 'benchmark', 'baseline', 'performance',
        'evaluation', 'assessment', 'measurement'
    ]
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
    
    # Check for code availability (0.3 points) - more comprehensive
    code_keywords = [
        'code', 'github', 'repository', 'script', 'notebook', 'jupyter',
        'source code', 'implementation', 'codebase', 'repository'
    ]
    if any(keyword in readme_lower for keyword in code_keywords):
        score += 0.3
    
    # Check for environment setup (0.3 points) - more comprehensive
    env_keywords = [
        'environment', 'requirements', 'dependencies', 'install', 'setup', 'docker',
        'conda', 'pip', 'package', 'library', 'framework', 'configuration'
    ]
    if any(keyword in readme_lower for keyword in env_keywords):
        score += 0.3
    
    # Check for reproducibility instructions (0.4 points) - more comprehensive
    repro_keywords = [
        'reproduce', 'reproducibility', 'replicate', 'replication', 'recreate',
        'step by step', 'instructions', 'tutorial', 'guide', 'experiment',
        'reproduce results', 'replication study'
    ]
    
    if any(keyword in readme_lower for keyword in repro_keywords):
        score += 0.4
    
    return min(1.0, score)


def dataset_quality_sub_score(model_id: str) -> Tuple[float, float]:
    """
    Calculate dataset quality sub-score based on README analysis.
    
    Evaluates the 5 criteria from the dataset quality requirements:
    - Documentation of the dataset (0.2 weight)
    - Clarity of the license (0.2 weight)
    - Safety/privacy considerations (0.2 weight)
    - Curation/quality control measures (0.2 weight)
    - Reproducibility (0.2 weight)
    
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
    
    # Calculate all 5 dataset quality scores
    doc_score = evaluate_dataset_documentation(readme)
    license_score = evaluate_license_clarity(readme)
    safety_score = evaluate_safety_privacy(readme)
    curation_score = evaluate_curation_quality(readme)
    repro_score = evaluate_reproducibility(readme)
    
    # Equal weighted combination (0.2 each for the 5 criteria)
    final_score = (
        doc_score * 0.2 +
        license_score * 0.2 +
        safety_score * 0.2 +
        curation_score * 0.2 +
        repro_score * 0.2
    )
    
    end_time = time.time()
    return (final_score, end_time - start_time)


if __name__ == "__main__":
    # Test with a sample model
    model_id = "google/gemma-2b"
    score, elapsed = dataset_quality_sub_score(model_id)
    print(f"Dataset quality score: {score:.3f} (elapsed: {elapsed:.3f}s)")
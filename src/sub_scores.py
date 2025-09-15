import re
import time
from typing import Optional

import requests

from .logging_config import get_logger, log_error_with_context, log_performance

# Initialize logger for this module
logger = get_logger(__name__)

# Define which licenses are compatible with LGPL v2.1
# This list is from two websites:
# https://huggingface.co/docs/hub/en/repositories-licenses for the codes
# https://www.gnu.org/licenses/license-list.html for compatibility
COMPATIBLE_LICENSES = {
    'gpl-2.0', 'gpl-3.0', 'lgpl-2.1', 'artistic-2.0', 'mit', 'bsl-1.0',
    'bsd-3-clause', 'cc0-1.0', 'cc-by-4.0', 'wtfpl', 'isc', 'ncsa',
    'unlicense', 'zlib',
}

"""
Fetch the README.md text from a Hugging Face model repository. Uses the
model URL. Checks if the given URL is for the model page or for
the code tree.
"""

def fetch_readme(model_url: str) -> Optional[str]:
    logger.debug(f"Fetching README from: {model_url}")

    # Convert tree/main URL into raw README URL
    if "tree/main" in model_url:
        base = model_url.split("tree/main")[0]
        raw_url = f"{base}resolve/main/README.md"
    else:
        raw_url = f"{model_url}/resolve/main/README.md"

    logger.debug(f"Converted to raw URL: {raw_url}")

    try:
        response = requests.get(raw_url, timeout=10)
        response.raise_for_status()
        logger.info(f"Successfully fetched README from {model_url}")
        return str(response.text)
    except Exception as e:
        log_error_with_context(e, f"Failed to fetch README from {model_url}", logger)
        return None

"""
Extract license information from a Hugging Face README.md file.
Handles both YAML front matter and '## License' sections.
(The example is a yaml but it says to look for a heading so I added both).
Doesn't use hugging face API.
"""

def extract_license(readme_text: str) -> Optional[str]:
    # Case 1: YAML front matter
    yaml_match = re.search(r"^---[\s\S]*?license:\s*([^\n]+)",
                           readme_text, re.IGNORECASE | re.MULTILINE)
    if yaml_match:
        return yaml_match.group(1).strip().lower()

    # Case 2: Markdown heading '## License'
    lines = readme_text.splitlines()
    for i, line in enumerate(lines):
        if re.match(r"^#+\s*License\s*$", line.strip(), re.IGNORECASE):
            for j in range(i + 1, len(lines)):
                if lines[j].strip():
                    return lines[j].strip().lower()

    return None

"""
Calculate license sub-score:
- 1 if license is present and compatible with LGPL v2.1
- 0 if not found or incompatible
"""

def license_sub_score(model_url: str) -> tuple[int, float]:
    start_time = time.time()
    logger.debug(f"Calculating license sub-score for: {model_url}")

    readme = fetch_readme(model_url)
    if not readme:
        logger.warning(f"No README found for {model_url}")
        end_time = time.time()
        log_performance("license_sub_score (no README)", end_time - start_time, logger)
        return (0, end_time - start_time)

    license_str = extract_license(readme)
    logger.debug(f"Extracted license: {license_str}")

    if not license_str:
        logger.warning(f"No license found in README for {model_url}")
        end_time = time.time()
        log_performance("license_sub_score (no license)", end_time - start_time, logger)
        return (0, end_time - start_time)

    # Normalize
    normalized = license_str.lower().replace(
        " ", "").replace("-", "").replace("license", "")

    for comp in COMPATIBLE_LICENSES:
        if comp.replace("-", "").replace(" ", "") in normalized:
            logger.info(f"Found compatible license '{comp}' for {model_url}")
            end_time = time.time()
            log_performance("license_sub_score (compatible)", end_time - start_time, logger)
            return (1, end_time - start_time)

    logger.info(f"No compatible license found for {model_url} (found: {license_str})")
    end_time = time.time()
    log_performance("license_sub_score (incompatible)", end_time - start_time, logger)
    return (0, end_time - start_time)

if __name__ == "__main__":
    url = "https://huggingface.co/baidu/ERNIE-4.5-21B-A3B-Thinking"
    print(license_sub_score(url))  # -> 1 if compatible, 0 otherwise

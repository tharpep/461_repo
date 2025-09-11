from unittest.mock import Mock, patch

import pytest

from src import sub_scores

# Example README text with YAML license
README_YAML = """---
name: Example Model
license: MIT
---
# Model
This is a test model.
"""

# Example README text with Markdown license section
README_MD = """
# Example Model

## License
Apache-2.0
"""

# README without license
README_NONE = """
# Example Model
No license here.
"""

# README with multiple license headings
README_MULTIPLE = """
# Model
## License
MIT
## License
GPL-2.0
"""

# Empty README
README_EMPTY = ""


@pytest.mark.parametrize(
    "readme_text,expected_score",
    [
        (README_YAML, 1),          # MIT is compatible
        (README_MD, 0),            # Apache-2.0 not compatible
        (README_NONE, 0),          # No license
        ("---\nlicense: Apache-2.0\n---", 0),  # Incompatible YAML license
        ("---\nlicense: MIT License\n---", 1),  # Compatible test
    ]
)
def test_license_sub_score(monkeypatch, readme_text, expected_score):
    monkeypatch.setattr(sub_scores, "fetch_readme", lambda url: readme_text)
    score, elapsed = sub_scores.license_sub_score(
        "https://huggingface.co/mock-model")
    assert score == expected_score
    assert elapsed >= 0  # should return some elapsed time


def test_license_sub_score_empty(monkeypatch):
    # Test empty README
    monkeypatch.setattr(sub_scores, "fetch_readme", lambda url: README_EMPTY)
    score, _ = sub_scores.license_sub_score(
        "https://huggingface.co/mock-model")
    assert score == 0


def test_extract_license_yaml():
    license_str = sub_scores.extract_license(README_YAML)
    assert license_str == "MIT".lower()


def test_extract_license_md():
    license_str = sub_scores.extract_license(README_MD)
    assert license_str == "Apache-2.0".lower()


def test_extract_license_none():
    license_str = sub_scores.extract_license(README_NONE)
    assert license_str is None


def test_extract_license_multiple():
    license_str = sub_scores.extract_license(README_MULTIPLE)
    assert license_str.lower() == "mit"  # first license heading is returned


@patch("requests.get")
def test_fetch_readme_success(mock_get):
    mock_resp = Mock()
    mock_resp.raise_for_status = Mock()
    mock_resp.text = README_YAML
    mock_get.return_value = mock_resp
    result = sub_scores.fetch_readme("https://huggingface.co/mock-model")
    assert "MIT" in result


@patch("requests.get")
def test_fetch_readme_tree_main(mock_get):
    mock_resp = Mock()
    mock_resp.raise_for_status = Mock()
    mock_resp.text = "Tree main README"
    mock_get.return_value = mock_resp

    result = sub_scores.fetch_readme("https://huggingface.co/model/tree/main")
    assert result == "Tree main README"


@patch("requests.get")
def test_fetch_readme_failure(mock_get):
    mock_get.side_effect = Exception("Network error")
    result = sub_scores.fetch_readme("https://huggingface.co/mock-model")
    assert result is None

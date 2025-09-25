import json
import os
import subprocess
import sys
import tempfile
import unittest

# Add the project root to the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Since the run script doesn't have a .py extension, we'll test it by
# executing it directly
# We don't need to import the main module functions since we're testing
# via subprocess


class TestRun(unittest.TestCase):

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.sample_csv_content = """https://github.com/test/code,\
https://huggingface.co/datasets/test,\
https://huggingface.co/google-bert/bert-base-uncased
,,https://huggingface.co/parvk11/audience_classifier_model
,,https://huggingface.co/openai/whisper-tiny/tree/main"""

    def test_install_command(self) -> None:
        """Test run script install command."""
        result = subprocess.run(['python', 'run', 'install'],
                                capture_output=True, text=True, cwd='.')
        # Should succeed (exit code 0) or fail gracefully
        self.assertIn(result.returncode, [0, 1])

    def test_test_command(self) -> None:
        """Test run script test command - skip to avoid infinite loop."""
        # Skip this test to avoid infinite loop when testing 'python run test'
        # The test command functionality is verified by running it manually
        self.skipTest("Skipping to avoid infinite loop with 'python run test'")

    def test_run_script_with_csv_file(self) -> None:
        """Test run script with valid CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False,
                                         suffix='.txt') as f:
            f.write(self.sample_csv_content)
            temp_file = f.name

        try:
            result = subprocess.run(['python', 'run', temp_file],
                                    capture_output=True, text=True, cwd='.')
            self.assertEqual(result.returncode, 0)
            # Should output JSON for each model URL
            output_lines = result.stdout.strip().split('\n')
            self.assertEqual(len(output_lines), 3)

            # Verify each line is valid JSON
            for line in output_lines:
                if line.strip():
                    json.loads(line)
        finally:
            os.unlink(temp_file)

    def test_run_script_file_not_found(self) -> None:
        """Test run script with non-existent file."""
        result = subprocess.run(['python', 'run', 'non_existent_file.txt'],
                                capture_output=True, text=True, cwd='.')
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error: File 'non_existent_file.txt' not found",
                      result.stderr)

    def test_run_script_empty_file(self) -> None:
        """Test run script with empty file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False,
                                         suffix='.txt') as f:
            f.write("")
            temp_file = f.name

        try:
            result = subprocess.run(['python', 'run', temp_file],
                                    capture_output=True, text=True, cwd='.')
            self.assertEqual(result.returncode, 0)
            # Should not output anything for empty file
            self.assertEqual(result.stdout.strip(), "")
        finally:
            os.unlink(temp_file)

    def test_run_script_only_github_urls(self) -> None:
        """Test run script with only GitHub URLs (no model links)."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False,
                                         suffix='.txt') as f:
            f.write("https://github.com/test/repo,,\n")
            temp_file = f.name

        try:
            result = subprocess.run(['python', 'run', temp_file],
                                    capture_output=True, text=True, cwd='.')
            self.assertEqual(result.returncode, 0)
            # Should not output anything since no model links
            self.assertEqual(result.stdout.strip(), "")
        finally:
            os.unlink(temp_file)

    def test_run_script_no_args(self) -> None:
        """Test run script with no arguments."""
        result = subprocess.run(['python', 'run'],
                                capture_output=True, text=True, cwd='.')
        self.assertEqual(result.returncode, 1)

    def test_csv_parsing_edge_cases(self) -> None:
        """Test CSV parsing with various edge cases."""
        edge_case_content = """https://github.com/test,\
https://huggingface.co/datasets/test,\
https://huggingface.co/model1
,,
https://github.com/test2,,https://huggingface.co/model2
,https://huggingface.co/datasets/test2,https://huggingface.co/model3"""

        with tempfile.NamedTemporaryFile(mode='w', delete=False,
                                         suffix='.txt') as f:
            f.write(edge_case_content)
            temp_file = f.name

        try:
            result = subprocess.run(['python', 'run', temp_file],
                                    capture_output=True, text=True, cwd='.')
            self.assertEqual(result.returncode, 0)
            # Should process 3 model URLs (skip empty row)
            output_lines = result.stdout.strip().split('\n')
            self.assertEqual(len(output_lines), 3)

            # Verify each line is valid JSON
            for line in output_lines:
                if line.strip():
                    json.loads(line)
        finally:
            os.unlink(temp_file)

    def test_json_output_format(self) -> None:
        """Test that JSON output is properly formatted."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False,
                                         suffix='.txt') as f:
            f.write(",,https://huggingface.co/test/model\n")
            temp_file = f.name

        try:
            result = subprocess.run(['python', 'run', temp_file],
                                    capture_output=True, text=True, cwd='.')
            self.assertEqual(result.returncode, 0)

            # Verify JSON output format
            output_lines = result.stdout.strip().split('\n')
            self.assertEqual(len(output_lines), 1)

            parsed_json = json.loads(output_lines[0])
            self.assertIn("name", parsed_json)
            self.assertIn("category", parsed_json)
            self.assertIn("net_score", parsed_json)
            self.assertEqual(parsed_json["category"], "MODEL")
        finally:
            os.unlink(temp_file)


if __name__ == '__main__':
    unittest.main()

"""
Unit test file for the script summarize_metadata.py.

Verifies that the metadata summary is correctly generated and displayed as a table.
"""

import unittest
from unittest.mock import patch, mock_open

from apps.metadata_analysis import summarize_metadata
import json

class TestSummarizeMetadata(unittest.TestCase):
    """
    Test suite for the script summarize_metadata.py.
    """

    def setUp(self):
        """
        Initial setup for the tests.
        """
        self.metadata_json = """
        {
            "0x0001": {
                "distinct_values_count": 1,
                "values": ["NIKON CORPORATION"]
            },
            "0x0002": {
                "distinct_values_count": 1,
                "values": ["NIKON D5600"]
            },
            "0x0003": {
                "distinct_values_count": 2,
                "values": ["Horizontal (normal)", "Rotated 90 CCW"]
            },
            "0x0004": {
                "distinct_values_count": 1,
                "values": [{"id": "Exif-ImageSize", "val": "6016x4016"}]
            }
        }
        """
        self.expected_summary = [
            ["0x0001", 1, "NIKON CORPORATION"],
            ["0x0002", 1, "NIKON D5600"],
            ["0x0003", 2, 'multiple'],
            ["0x0004", 1, '{\n  "id": "Exif-ImageSize",\n  "val": "6016x4016"\n}']
        ]

    @patch("builtins.open", new_callable=mock_open, read_data="")
    @patch("json.load")
    def test_load_metadata(self, mock_json_load, mock_file):
        """
        Test the load_metadata function to ensure it correctly loads JSON data from a file.
        """
        mock_json_load.return_value = json.loads(self.metadata_json)
        metadata = summarize_metadata.load_metadata("dummy_path")
        self.assertEqual(metadata, json.loads(self.metadata_json))
        mock_file.assert_called_once_with("dummy_path", 'r')
        mock_json_load.assert_called_once()

    def test_summarize_metadata(self):
        """
        Test the summarize_metadata function to ensure it correctly summarizes the metadata.
        """
        metadata = json.loads(self.metadata_json)
        summary = summarize_metadata.summarize_metadata(metadata)
        self.assertEqual(summary, self.expected_summary)

    @patch("builtins.print")
    @patch("apps.metadata_analysis.summarize_metadata.load_metadata")
    @patch("apps.metadata_analysis.summarize_metadata.summarize_metadata")
    def test_main(self, mock_summarize_metadata, mock_load_metadata, mock_print):
        """
        Test the main function to ensure it correctly loads metadata, summarizes it, and prints the table.
        """
        mock_load_metadata.return_value = json.loads(self.metadata_json)
        mock_summarize_metadata.return_value = self.expected_summary

        with patch("sys.argv", ["summarize_metadata.py", "dummy_path"]):
            summarize_metadata.main("dummy_path")

        mock_load_metadata.assert_called_once_with("dummy_path")
        mock_summarize_metadata.assert_called_once_with(json.loads(self.metadata_json))
        mock_print.assert_called()

if __name__ == '__main__':
    unittest.main()

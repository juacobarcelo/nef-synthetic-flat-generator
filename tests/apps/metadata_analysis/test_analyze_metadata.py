"""
Unit test file for the module analyze_metadata.py.

Verifies that the metadata extraction and analysis functions work correctly.
"""

import unittest
from apps.metadata_analysis.analyze_metadata import extract_metadata, analyze_metadata

class TestAnalyzeMetadata(unittest.TestCase):
    """
    Test suite for the module analyze_metadata.py.
    """

    def setUp(self):
        """
        Initial setup for the tests.
        """
        # Simulate metadata extracted from NEF files
        self.metadata_list = [
            {'Make': 'Nikon', 'Model': 'D5300', 'ISO': '400', 'ExposureTime': '1/60'},
            {'Make': 'Nikon', 'Model': 'D5300', 'ISO': '800', 'ExposureTime': '1/125'},
            {'Make': 'Nikon', 'Model': 'D5300', 'ISO': '400', 'ExposureTime': '1/60'}
        ]

    def test_analyze_metadata(self):
        """
        Test the analyze_metadata function to verify metadata variability.
        """
        analysis = analyze_metadata(self.metadata_list)

        # Verify that the 'Make' field has only one distinct value
        self.assertEqual(analysis['Make']['distinct_values_count'], 1)
        self.assertListEqual(analysis['Make']['values'], ['Nikon'])

        # Verify that the 'ISO' field has two distinct values
        self.assertEqual(analysis['ISO']['distinct_values_count'], 2)
        self.assertCountEqual(analysis['ISO']['values'], ['400', '800'])

        # Verify that the 'ExposureTime' field has two distinct values
        self.assertEqual(analysis['ExposureTime']['distinct_values_count'], 2)
        self.assertCountEqual(analysis['ExposureTime']['values'], ['1/60', '1/125'])

    def test_extract_metadata(self):
        """
        Test the extract_metadata function with a simulated NEF file.
        """
        # This test would require a real NEF file or a mock. Left as pending.
        pass  # Implement tests with mocks if necessary

if __name__ == '__main__':
    unittest.main()

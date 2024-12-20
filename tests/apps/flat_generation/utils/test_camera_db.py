"""
Unit tests for camera database functionality and Bayer pattern conversion.
"""

import json
import pytest
from apps.flat_generation.utils.camera_db import BayerPatternConverter, CameraDB
from apps.flat_generation.utils.camera_db import extract_metadata
import yaml
import tempfile
import os
from unittest.mock import patch, Mock

# Test data for camera database

SAMPLE_DB_DATA_NIKON = """
- camera:
    exiftool_properties:
      - group: EXIF
        Make: NIKON CORPORATION
      - group: EXIF
        Model: NIKON D5600
    bayer_pattern:
      - group: EXIF
        name: CFAPattern
    master_flat_metadata:
      - group: EXIF
        name: CFAPattern
      - group: MakerNotes
        name: WhiteBalance
"""

SAMPLE_DB_DATA_CANON = """
- camera:
    exiftool_properties:
      - group: EXIF
        Make: CANON
      - group: EXIF
        Model: EOS 80D
    bayer_pattern:
      - group: EXIF
        name: CFAPattern
    master_flat_metadata:
      - group: EXIF
        name: CFAPattern
      - group: MakerNotes
        name: WhiteBalance
"""

SAMPLE_DB_DATA = yaml.dump(yaml.safe_load(SAMPLE_DB_DATA_NIKON) + yaml.safe_load(SAMPLE_DB_DATA_CANON))



# Sample exiftool output for testing
SAMPLE_EXIFTOOL_OUTPUT_KEYS_NOT_INCLUDED_IN_MASTER_FLAT_METADATA = {
    "OTHER_GROUP_0:KEY_NOT_INCLUDED_IN_MASTER_FLAT_METADATA_0": "OTHER_VALUE_0",
    "OTHER_GROUP_1:KEY_NOT_INCLUDED_IN_MASTER_FLAT_METADATA_1": "OTHER_VALUE_1"
}

SAMPLE_EXIFTOOL_OUTPUT_NIKON__KEYS_INCLUDED_IN_MASTER_FLAT_METADATA = {
    "EXIF:CFAPattern": "RGGB",
    "MakerNotes:WhiteBalance": "Auto"
}

SAMPLE_EXIFTOOL_OUTPUT_CANON__KEYS_INCLUDED_IN_MASTER_FLAT_METADATA = {
    "EXIF:CFAPattern": "BGGR",
    "MakerNotes:WhiteBalance": "Manual"
}

SAMPLE_EXIFTOOL_PROPERTIES_NIKON = {
    "EXIF:Make": "NIKON CORPORATION",
    "EXIF:Model": "NIKON D5600"
}

SAMPLE_EXIFTOOL_PROPERTIES_CANON = {
    "EXIF:Make": "CANON",
    "EXIF:Model": "EOS 80D"
}

SAMPLE_EXIFTOOL_OUTPUT_NIKON = SAMPLE_EXIFTOOL_PROPERTIES_NIKON | SAMPLE_EXIFTOOL_OUTPUT_NIKON__KEYS_INCLUDED_IN_MASTER_FLAT_METADATA | SAMPLE_EXIFTOOL_OUTPUT_KEYS_NOT_INCLUDED_IN_MASTER_FLAT_METADATA
SAMPLE_EXIFTOOL_OUTPUT_CANON = SAMPLE_EXIFTOOL_PROPERTIES_CANON | SAMPLE_EXIFTOOL_OUTPUT_CANON__KEYS_INCLUDED_IN_MASTER_FLAT_METADATA | SAMPLE_EXIFTOOL_OUTPUT_KEYS_NOT_INCLUDED_IN_MASTER_FLAT_METADATA

class TestBayerPatternConverter:
    """Tests for BayerPattern conversion functionality."""

    @pytest.mark.parametrize("input_pattern,expected", [
        ("[Red,Green][Green,Blue]", "RGGB"),
        ("[Red,Blue][Green,Blue]", "RBGB"),
        ("[Blue,Green][Green,Red]", "BGGR"),
        ("[Red,Green][Blue,Green]", "RGBG"),
        ("[Green,Red][Red,blue]", "GRRB"),
        ("[rEd,grEEn][greeN,bLue]", "RGGB"),
        ("[0,1,1,2]", "RGGB"),
        ("[1,0,1,2]", "GRGB"),
        ("0 1 1 2", "RGGB"),
        ("0 2 2 1", "RBBG"),
        ("RGGB", "RGGB"),
        ("BGBR", "BGBR"),
        ("rggb", "RGGB"),
        ("0112", "RGGB"),
        ("[R,G][G,B]", "RGGB"),
        ("[g,B][B,r]", "GBBR"),
        ("R G G B", "RGGB"),
        ("b r r g", "BRRG"),
    ])
    def test_standardize_pattern_formats(self, input_pattern, expected):
        """Test different input formats for Bayer pattern conversion."""
        result = BayerPatternConverter.standardize_pattern(input_pattern)
        assert result == expected

    @pytest.mark.parametrize("invalid_input_pattern",
        ["[Red,Green][Green,Blue,Red]", 
         "[Red,Green][Green]", 
         "RGBBR", 
         "RGB", 
         "1234",
         "12",
         "[1,2]"
        ])
    def test_invalid_numeric_pattern(self, invalid_input_pattern):
        """Test handling of invalid numeric patterns."""
        with pytest.raises(KeyError):
            BayerPatternConverter.standardize_pattern(invalid_input_pattern)




class TestCameraDB:
    """Tests for CameraDB functionality."""

    @pytest.fixture
    def temp_db_file(self):
        """Create a temporary database file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            f.write(SAMPLE_DB_DATA)
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.fixture
    def camera_db(self, temp_db_file):
        """Create a CameraDB instance with test data."""
        return CameraDB(temp_db_file)

    def test_load_db(self, camera_db):
        """Test database loading."""
        assert len(camera_db.db_data) == 2
        assert camera_db.db_data[0]['camera']['exiftool_properties'][0]['Make'] == "NIKON CORPORATION"
        assert camera_db.db_data[1]['camera']['exiftool_properties'][0]['Make'] == "CANON"

    @pytest.mark.parametrize("sample_output", [
        SAMPLE_EXIFTOOL_OUTPUT_NIKON,
        SAMPLE_EXIFTOOL_OUTPUT_CANON
    ])
    @patch('apps.flat_generation.utils.camera_db.subprocess.run')
    def test_extract_metadata(self, mock_run, camera_db, sample_output):
        """Test metadata extraction from file."""
        mock_process = Mock()
        mock_process.stdout = json.dumps([sample_output])
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        metadata = extract_metadata("dummy.nef")
        assert metadata == sample_output
        

    @pytest.mark.parametrize("sample_output,expected_camera_data", [
        (SAMPLE_EXIFTOOL_OUTPUT_NIKON, yaml.safe_load(SAMPLE_DB_DATA_NIKON)[0]['camera']),
        (SAMPLE_EXIFTOOL_OUTPUT_CANON, yaml.safe_load(SAMPLE_DB_DATA_CANON)[0]['camera'])
    ])
    @patch('apps.flat_generation.utils.camera_db.extract_metadata')
    def test_get_camera_config(self, mock_get_metadata, camera_db, sample_output, expected_camera_data):
        """Test get_camera_config method."""
        mock_get_metadata.return_value = sample_output
        config = camera_db.get_camera_config("dummy.nef")
        assert config == expected_camera_data

    @pytest.mark.parametrize("sample_output,expected_pattern", [
        (SAMPLE_EXIFTOOL_OUTPUT_NIKON, "RGGB"),
        (SAMPLE_EXIFTOOL_OUTPUT_CANON, "BGGR")
    ])
    @patch('subprocess.run')
    def test_get_bayer_pattern(self, mock_run, camera_db, sample_output, expected_pattern):
        """Test Bayer pattern retrieval."""
        import subprocess  # Import subprocess within the test

        mock_process = Mock()
        mock_process.stdout = json.dumps([sample_output])
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        pattern = camera_db.get_bayer_pattern("dummy.nef")
        assert pattern == expected_pattern

    @pytest.mark.parametrize("sample_output,expected_metadata", [
        (SAMPLE_EXIFTOOL_OUTPUT_NIKON, {"EXIF:CFAPattern": "RGGB", "MakerNotes:WhiteBalance": "Auto"}),
        (SAMPLE_EXIFTOOL_OUTPUT_CANON, {"EXIF:CFAPattern": "BGGR", "MakerNotes:WhiteBalance": "Manual"})
    ])
    @patch('subprocess.run')
    def test_get_master_flat_metadata(self, mock_run, camera_db, sample_output, expected_metadata):
        """Test master flat metadata retrieval."""
        import subprocess  # Import subprocess within the test

        mock_process = Mock()
        mock_process.stdout = json.dumps([sample_output])
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        metadata = camera_db.get_master_flat_metadata("dummy.nef")
        assert metadata == expected_metadata

    

    @pytest.mark.parametrize("mismatched_metadata", [
        {
            "EXIF:Make": "CANON",
            "EXIF:Model": "NOT DEFINED MODEL",
            "EXIF:CFAPattern": "RGGB",
            "MakerNotes:WhiteBalance": "Auto"
        },
        {
            "EXIF:Make": "SONY",
            "EXIF:Model": "NOT DEFINED MODEL",
            "EXIF:CFAPattern": "BGGR",
            "MakerNotes:WhiteBalance": "Manual"
        },
        {
            "EXIF:Make": "FUJI",
            "EXIF:Model": "NOT DEFINED MODEL",
            "EXIF:CFAPattern": "GBRG",
            "MakerNotes:WhiteBalance": "Daylight"
        },
        {
            "EXIF:Make": "NIKON CORPORATION",
            "EXIF:Model": "NOT DEFINED MODEL"
        },
        {
            "EXIF:Make": "NOT DEFINED MAKE",
            "EXIF:Model": "NIKON D5600"
        },
        {
            "NOT_DEFINED_GROUP:Make": "NIKON CORPORATION",
            "EXIF:Model": "NIKON D5600"
        },
        {
            "EXIF:Make": "NIKON CORPORATION",
            "EXIF:NOT_DEFINED_KEY": "NIKON D5600"
        }
    ])
    @patch('subprocess.run')
    def test_camera_config_mismatch(self, mock_run, camera_db, mismatched_metadata):
        """Test behavior when exiftool_properties do not match."""
        import subprocess  # Import subprocess within the test

        mock_process = Mock()
        mock_process.stdout = json.dumps([mismatched_metadata])
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        config = camera_db.get_camera_config("dummy.nef")
        assert config is None

    def test_db_file_not_found(self):
        """Test behavior when database file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            CameraDB("nonexistent.yaml")


    # TODO: test get_master_flat_metadata() considering different cases of allow_subset_of_defined_flat_metadata parameter
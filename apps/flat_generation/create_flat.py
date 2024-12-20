"""
Module for generating synthetic flat frames in DNG format from NEF files.

This script processes pixel data from NEF files, applies star removal and smoothing
techniques, and generates a DNG file compatible with RawTherapee.
"""

import json
import argparse
import tempfile
import shutil
import glob
from pathlib import Path
import logging
from typing import List, Dict

from utils.raw_utils import read_raw_data, extract_bayer_channels, combine_channels
from utils.camera_db import CameraDB, BayerPatternConverter
from apps.metadata_analysis.analyze_metadata import extract_metadata

def setup_logging():
    """Configure logging settings."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def create_temp_directory() -> str:
    """
    Create a temporary directory for intermediate files.

    Returns:
        str: Path to the created temporary directory.
    """
    temp_dir = tempfile.mkdtemp(prefix='synthetic_flat_')
    logging.info(f"Created temporary directory: {temp_dir}")
    return temp_dir

def get_nef_files(input_directory: str) -> List[str]:
    """
    Get all NEF files from the input directory.

    Args:
        input_directory (str): Directory containing NEF files.

    Returns:
        List[str]: List of paths to NEF files.
    """
    nef_files = glob.glob(Path(input_directory, "*.NEF").as_posix())
    if not nef_files:
        raise ValueError(f"No NEF files found in {input_directory}")
    return nef_files

def read_config(config_file: str) -> Dict:
    """
    Read and parse a JSON configuration file.

    Args:
        config_file (str): Path to the configuration file.

    Returns:
        Dict: Configuration data.
    """
    with open(config_file, 'r') as f:
        return json.load(f)

def main(args):
    """
    Main function for synthetic flat generation.

    Args:
        args: Parsed command line arguments.
    """
    setup_logging()
    temp_dir = create_temp_directory()
    
    try:
        nef_files = get_nef_files(args.input_directory)
        logging.info(f"Found {len(nef_files)} NEF files")
        
        # Initialize camera database 
        camera_db = CameraDB('./camera_db.yaml')
        logging.info("Using camera database for metadata configuration")
        

        # Determine master flat metadata. Check that final output metadata coming from each NEF file is consistent (e.g., same ISO, exposure time, etc.)
        # If not, raise an error. 
        # Consistency: each image file should have the same metadata value for each key defined in the camera database.
        # Also assure that bayern pattern is consistent across all files.
        master_flat_metadata = {}
        bayer_pattern = None
        for nef_file in nef_files:
            logging.info(f"Extracting metadata from {nef_file}")
            # Extract metadata required for master flat defined in camera_db database. Extraction is strict: if any metadata is missing, raise an error.
            final_metadata_form_camera_db = camera_db.get_master_flat_metadata(nef_file, allow_subset_of_defined_flat_metadata=False)        
            if not master_flat_metadata:
                master_flat_metadata = final_metadata_form_camera_db
            else:
                # check that every value in the dictionary is the same
                inconsistent_metadata_value = { 
                                                key: {
                                                        'file': nef_file, 
                                                        'expected': master_flat_metadata[key], 
                                                        'found': final_metadata_form_camera_db[key]
                                                    }
                                                for key, value in final_metadata_form_camera_db.items()
                                                if master_flat_metadata[key] != value
                                            }
                if inconsistent_metadata_value:
                    raise ValueError(f"Metadata inconsistency found in {nef_file}: {inconsistent_metadata_value}")
            
            # Bayer pattern
            file_bayer_pattern = BayerPatternConverter.standardize_pattern(camera_db.get_bayer_pattern(nef_file))
            if not bayer_pattern:
                bayer_pattern = BayerPatternConverter.standardize_pattern( )
            else:
                # Check that Bayer pattern is consistent across all files
                if bayer_pattern != file_bayer_pattern:
                    raise ValueError(f"Bayer pattern inconsistency found in {nef_file}. Expected: {bayer_pattern}, Found: {file_bayer_pattern}")

        
        logging.info(f"Master flat metadata: {master_flat_metadata}")
        logging.info(f"Bayer pattern: {bayer_pattern}")
        
        
        # Process files
        channel_data = {'R': [], 'G': [], 'B': []}
        for nef_file in nef_files:
            raw_data = read_raw_data(nef_file)
            channels = extract_bayer_channels(raw_data, pattern=bayer_pattern)
            
            for channel in ['R', 'G', 'B']:
                channel_data[channel].append(channels[channel])
        
        # Process accumulated channel data and create final flat
        # ... (Additional processing code will go here)
        
        # Create output DNG file
        # ... (DNG creation code will go here)
        
    finally:
        if not args.debug:
            # Clean up temporary directory if not in debug mode
            shutil.rmtree(temp_dir)
            logging.info(f"Cleaned up temporary directory: {temp_dir}")
        else:
            logging.info(f"Debug mode: Temporary directory preserved at {temp_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic flat frame from NEF files")
    parser.add_argument("input_directory", help="Directory containing NEF files")
    parser.add_argument("--bayer_pattern", help="Bayer pattern to use (e.g., RGGB, [0,1,1,2])")
    parser.add_argument("output_path", help="Path for output DNG file")
    parser.add_argument("--debug", action="store_true", help="Preserve temporary files for debugging")
    
    args = parser.parse_args()
    main(args)
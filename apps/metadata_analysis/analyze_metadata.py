"""
Module for analyzing metadata of NEF files.

This script extracts and analyzes metadata from NEF files in a given directory,
identifying stable and variable fields, and generates a structured report.
"""

import json
import argparse
from collections import defaultdict
import multiprocessing
from pathlib import Path

from apps.metadata_analysis.extract_metadata import extract_metadata


def main(input_directory: str, output_file: str):
    """
    Main entry point for metadata analysis.

    Iterates over all NEF files in the input directory, extracts metadata in parallel,
    and generates a report on the variability of each metadata field.

    Args:
        input_directory (str): Directory containing the NEF files.
        output_file (str): Path to save the metadata analysis report.
    """
    # List all NEF files in the input directory
    input_path = Path(input_directory)
    nef_files = [file for file in input_path.glob('*.nef')]

    # Use multiprocessing to extract metadata in parallel
    with multiprocessing.Pool() as pool:
        metadata_list = pool.map(extract_metadata, nef_files)
    
    # Analyze the variability of the metadata
    analysis_result = analyze_metadata(metadata_list)
    
    # Save the report in JSON format
    output_path = Path(output_file)
    with output_path.open('w') as json_file:
        json.dump(analysis_result, json_file, indent=4)



def analyze_metadata(metadata_list: list) -> dict:
    """
    Analyzes the variability of the extracted metadata.

    For each metadata field, determines the number of distinct values
    and lists those values.

    Args:
        metadata_list (list): List of metadata dictionaries.

    Returns:
        dict: Structured report on the variability of the metadata.
    """
    field_values = defaultdict(set)

    # Compile all values per field
    for metadata in metadata_list:
        for key, value in metadata.items():
            # Convert dictionary values to strings
            if isinstance(value, dict):
                value = json.dumps(value, sort_keys=True)
            field_values[key].add(value)
    
    analysis = {}
    for field, values in field_values.items():
        analysis[field] = {
            'distinct_values_count': len(values),
            'values': list(values)
        }
    return analysis

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze metadata of NEF files.")
    parser.add_argument("input_directory", help="Directory containing the NEF files.")
    parser.add_argument("output_file", help="Path to save the metadata report.")
    args = parser.parse_args()

    main(args.input_directory, args.output_file)
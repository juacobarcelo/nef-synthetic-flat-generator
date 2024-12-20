"""
Script to summarize metadata from a JSON file.

This script reads a JSON file containing metadata analysis results and displays a summary
as a table with the following columns: metadata, distinct_values_count, and value.
If there are multiple values for a metadata field, it will display 'multiple' instead of listing all values.

Usage:
    python summarize_metadata.py <metadata_file>

Args:
    metadata_file (str): Path to the JSON file containing metadata analysis results.
"""

import json
import sys
from tabulate import tabulate

def load_metadata(file_path: str) -> dict:
    """
    Loads metadata from a JSON file.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        dict: Dictionary containing the metadata analysis results.
    """
    with open(file_path, 'r') as file:
        metadata = json.load(file)
    return metadata

def format_value(value):
    """
    Formats the metadata value for better readability.

    Args:
        value: The metadata value to format.

    Returns:
        str: The formatted value.
    """
    if isinstance(value, dict):
        return json.dumps(value, indent=2)
    elif isinstance(value, list):
        if len(value) > 1:
            # Extract keys from the first dictionary in the list to show the "signature"
            if isinstance(value[0], dict):
                keys = ', '.join(value[0].keys())
                return f'multiple: {{"{keys}"}}'
            return 'multiple'
        else:
            return str(value[0])
    else:
        return str(value)

def summarize_metadata(metadata: dict) -> list:
    """
    Summarizes the metadata into a table format.

    Args:
        metadata (dict): Dictionary containing the metadata analysis results.

    Returns:
        list: List of lists representing the table rows.
    """
    summary = []
    for key, value in sorted(metadata.items()):
        distinct_values_count = value['distinct_values_count']
        values = value['values']
        
        if distinct_values_count > 1:
            value_display = format_value(values)
        else:
            value_display = format_value(values[0])
        
        summary.append([key, distinct_values_count, value_display])
    return summary

def main(metadata_file: str):
    """
    Main function to load metadata and display the summary table.

    Args:
        metadata_file (str): Path to the JSON file containing metadata analysis results.
    """
    metadata = load_metadata(metadata_file)
    summary = summarize_metadata(metadata)
    print(tabulate(summary, headers=['Metadata', 'Distinct Values Count', 'Value'], tablefmt='simple'))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python summarize_metadata.py <metadata_file>")
        sys.exit(1)
    
    metadata_file = sys.argv[1]
    main(metadata_file)

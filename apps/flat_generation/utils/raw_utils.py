"""
Utility functions for extracting and manipulating RAW data from NEF files.
Includes functions for reading raw data without demosaicing and extracting Bayer channels.
"""

import rawpy
import numpy as np

def read_raw_data(nef_file: str) -> np.ndarray:
    """
    Read RAW data from a NEF file without applying demosaicing.

    Args:
        nef_file (str): Path to the NEF file.

    Returns:
        numpy.ndarray: RAW data from the file.
    """
    with rawpy.imread(nef_file) as raw:
        raw_data = raw.raw_image.copy()
    return raw_data

def extract_bayer_channels(raw_data: np.ndarray, pattern: str = 'RGGB') -> dict:
    """
    Extract individual channels from the Bayer pattern.

    Args:
        raw_data (numpy.ndarray): RAW data from NEF file.
        pattern (str): Bayer pattern (default: 'RGGB').

    Returns:
        dict: Dictionary with extracted 'R', 'G', 'B' channels.
    """
    height, width = raw_data.shape
    channels = {}
    
    # Extract channels based on Bayer pattern
    channels['R'] = raw_data[0::2, 0::2]  # Top-left pixels
    channels['B'] = raw_data[1::2, 1::2]  # Bottom-right pixels
    
    # Combine both green channels
    G1 = raw_data[0::2, 1::2]  # Top-right pixels
    G2 = raw_data[1::2, 0::2]  # Bottom-left pixels
    channels['G'] = np.stack([G1, G2])
    
    return channels

def combine_channels(channel_data: dict, pattern: str = 'RGGB') -> np.ndarray:
    """
    Combine processed channels back into a Bayer pattern.

    Args:
        channel_data (dict): Dictionary with processed 'R', 'G', 'B' channels.
        pattern (str): Bayer pattern (default: 'RGGB').

    Returns:
        numpy.ndarray: Combined image in Bayer pattern.
    """
    height = channel_data['R'].shape[0] * 2
    width = channel_data['R'].shape[1] * 2
    result = np.zeros((height, width), dtype=np.float32)
    
    result[0::2, 0::2] = channel_data['R']
    result[1::2, 1::2] = channel_data['B']
    result[0::2, 1::2] = channel_data['G'][0]
    result[1::2, 0::2] = channel_data['G'][1]
    
    return result
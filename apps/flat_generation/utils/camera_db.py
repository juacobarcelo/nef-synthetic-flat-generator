"""
Utility for handling camera database operations and Bayer pattern management.
"""

from pydantic import BaseModel
import yaml
import re
from typing import List, Dict, Optional, Union
import subprocess
import json

from apps.metadata_analysis.extract_metadata import extract_metadata




class BayerPatternConverter:
    """Handles different Bayer pattern format conversions."""
    
    PATTERN_MAP = {
        # Numeric mappings
        '0': 'R', '1': 'G', '2': 'B',
        # Single letter mappings
        'R': 'R', 'G': 'G', 'B': 'B',
        # Full word mappings
        'RED': 'R', 'GREEN': 'G', 'BLUE': 'B'
    }

    @classmethod
    def standardize_pattern(cls, pattern: str) -> str:
        """
        Convert various Bayer pattern formats to standard RGGB format.
        
        Args:
            pattern (str): Input pattern in various formats:
                          - [Red,Green][Green,Blue]
                          - [0,1,1,2]
                          - 0 1 1 2
                          - RGGB
                          - R G G B
        
        Returns:
            str: Standardized pattern in RGGB format
        
        Raises:
            KeyError: If pattern contains invalid characters or numbers
        """
        # Remove special characters and whitespace and convert to uppercase
        clean_pattern = re.sub(r'[\[\],\s]', '', pattern).upper()
        
        # Handle numeric format
        if all(c in '012' for c in clean_pattern):
            if any(c not in '012' for c in clean_pattern):
                raise KeyError(f"Invalid numeric pattern: {pattern}")
            if len(clean_pattern) != 4:
                raise KeyError(f"Invalid numeric pattern length: {pattern} (must represent 4 positions)")
            return ''.join(cls.PATTERN_MAP[c] for c in clean_pattern)
        
        # Handle word-based format (Red, Green, Blue)
        result = ''
        current_word = ''
        
        i = 0
        while i < len(clean_pattern):
            char = clean_pattern[i]
            
            # Check if this is the start of a full word (RED, GREEN, BLUE)
            is_word_start = any(word.startswith(char) for word in ['RED', 'GREEN', 'BLUE'])
            
            if is_word_start:
                current_word = char
                # Look ahead for the rest of the word
                next_i = i + 1
                while next_i < len(clean_pattern):
                    next_char = clean_pattern[next_i]
                    temp_word = current_word + next_char
                    if any(word.startswith(temp_word) for word in ['RED', 'GREEN', 'BLUE']):
                        current_word = temp_word
                        next_i += 1
                    else:
                        break
                
                # Try to match the collected word
                if current_word in cls.PATTERN_MAP:
                    result += cls.PATTERN_MAP[current_word]
                    i = next_i
                else:
                    # No match found, try single character
                    if char in cls.PATTERN_MAP:
                        result += cls.PATTERN_MAP[char]
                    else:
                        raise KeyError(f"Invalid pattern component: {char}")
                    i += 1
                current_word = ''
            else:
                # Handle single character
                if char in cls.PATTERN_MAP:
                    result += cls.PATTERN_MAP[char]
                else:
                    raise KeyError(f"Invalid pattern component: {char}")
                i += 1
        
        # Check if there's any unprocessed part
        if current_word:
            raise KeyError(f"Invalid pattern component: {current_word}")
        
        # Verify we have a valid pattern length
        if len(result) != 4:
            raise KeyError(f"Invalid pattern length: {pattern} (must represent 4 positions)")
            
        return result



class CameraDB:
    """Handles camera database operations and metadata management."""
    
    def __init__(self, db_path: str):
        """
        Initialize CameraDB with database file path.
        
        Args:
            db_path (str): Path to camera database YAML file.
        """
        self.db_path = db_path
        self.db_data = self._load_db()

    def _load_db(self) -> List[Dict]:
        """Load and parse camera database file."""
        with open(self.db_path, 'r') as f:
            return yaml.safe_load(f)

    

    def get_camera_config(self, nef_file: str) -> Optional[Dict]:
        """
        Get camera configuration based on NEF file metadata.
        
        Args:
            nef_file (str): Path to NEF file.
            
        Returns:
            Optional[Dict]: Camera configuration if found, None otherwise.
        """
        file_metadata = extract_metadata(nef_file)
        
        for camera in self.db_data:
            if self._matches_camera(file_metadata, camera['camera']['exiftool_properties']):
                return camera['camera']
        return None

    

    def _matches_camera(self, metadata: Dict, properties: List[Dict]) -> bool:
        """Check if metadata matches camera properties.
        
        Args:
            metadata (Dict): Metadata to check.
            properties (List[Dict]): Camera properties to match.

        Returns:
            bool: True if all properties match, False otherwise
        """
        
        def transform_exiftool_properties_to_dict(properties: List[Dict]) -> Dict:
            """Transform exiftool properties to a dict.
                Each key ias a group:key and the value is the value of the key.
            
                Example:
                    - group: EXIF
                        Make: NIKON CORPORATION
                    - group: EXIF
                        Model: NIKON D5600
                Returns:
                    {'EXIF:Make': 'NIKON CORPORATION', 'EXIF:Model': 'NIKON D5600'}
                        
            """
            result = {}
            for prop in properties:
                group = prop['group']
                for key, value in prop.items():
                    if key == 'group':
                        continue
                    result[f"{group}:{key}"] = value
            return result
        matched_keys = set()
        metadata_dict = transform_exiftool_properties_to_dict(properties)
        
        # check that  boths dictionaries have the same keys and values
        for key, value in metadata_dict.items():
            if metadata.get(key) == value:
                matched_keys.add(key)
            
        return len(matched_keys) == len(metadata_dict)
        

    def get_bayer_pattern(self, nef_file: str) -> Optional[str]:
        """Get Bayer pattern for specified NEF file."""
        camera_config = self.get_camera_config(nef_file)
        if not camera_config:
            return None
            
        metadata = extract_metadata(nef_file)
        pattern_config = camera_config['bayer_pattern'][0]
        pattern_key = f"{pattern_config['group']}:{pattern_config['name']}"
        
        return metadata.get(pattern_key)

    def get_master_flat_metadata(self, nef_file: str, allow_subset_of_defined_flat_metadata: bool = True) -> Dict:
        """Get metadata fields to be included in master flat

        Args:
            nef_file (str): Path to NEF file.
            allow_subset_of_defined_flat_metadata (bool): If True, allow a subset of the defined flat metadata fields to be used.
                                                        If False, then all the defined flat metadata in database_db must be present in the NEF file metadata.

        
        Returns:
            Dict: Metadata fields to be included in master flat

        """
        camera_config = self.get_camera_config(nef_file)
        if not camera_config:
            return {}
            
        metadata = extract_metadata(nef_file)
        result = {}
        
        for field in camera_config['master_flat_metadata']:
            key = f"{field['group']}:{field['name']}"
            if key in metadata:
                result[key] = metadata[key]

        if not allow_subset_of_defined_flat_metadata and not(len(camera_config['master_flat_metadata']) == len(result)):
            raise ValueError(f"Missing metadata fields in NEF file: {nef_file}. Missing fields: {set(camera_config['master_flat_metadata']) - set(result)}")
        
        return result

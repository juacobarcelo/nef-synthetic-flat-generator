import json
from pathlib import Path
import subprocess
from typing import Union

from pydantic import BaseModel, model_validator





def extract_metadata(nef_file: Path) -> dict:
    """
    Extracts metadata from a NEF file using exiftool with detailed parameters.

    Args:
        nef_file (Path): Path to the NEF file.

    Returns:
        dict: Dictionary with the extracted metadata.
    """
    metadata = {}

    # Call exiftool to extract detailed metadata
    result = subprocess.run(['exiftool', '-G', '-s', '-H', '-a', '-u', '-json', str(nef_file)], capture_output=True, text=True)
    if result.returncode == 0:
        metadata_list = json.loads(result.stdout)
        if metadata_list:
            metadata = metadata_list[0]

    return metadata
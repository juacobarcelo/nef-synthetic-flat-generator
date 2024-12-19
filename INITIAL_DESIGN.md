# Initial Design Document

## Table of Contents

1. [Introduction](#introduction)
2. [System Overview](#system-overview)
3. [Requirements](#requirements)
   - [Functional Requirements](#functional-requirements)
   - [Non-Functional Requirements](#non-functional-requirements)
4. [Architecture](#architecture)
   - [High-Level Architecture](#high-level-architecture)
   - [Directory Structure](#directory-structure)
5. [Module Details](#module-details)
   - [Metadata Analysis Module](#metadata-analysis-module)
   - [Synthetic Flat Generation Module](#synthetic-flat-generation-module)
6. [Star Removal Framework](#star-removal-framework)
7. [Configuration Files](#configuration-files)
   - [Metadata List File](#metadata-list-file)
   - [Process Parameters File](#process-parameters-file)
8. [Implementation Guidelines](#implementation-guidelines)
   - [Libraries and Dependencies](#libraries-and-dependencies)
   - [Data Formats](#data-formats)
   - [Class Structure](#class-structure)
   - [Error Handling and Logging](#error-handling-and-logging)
9. [Future Extensions](#future-extensions)

---

## 1. Introduction

This document outlines the initial design for the NEF Synthetic Flat Generator software. It provides an exhaustive description of the system's design, including requirements, architecture, modules, and implementation details. The document serves as both a design reference and a practical guide for programmers implementing the software.

The software has two main purposes:

1. Analyze metadata from NEF (Nikon RAW) files to characterize variability across fields.
2. Generate synthetic flat frames in DNG format using advanced pixel-level manipulation techniques, ensuring compatibility with astrophotography workflows like RawTherapee.

---

## 2. System Overview

The system is composed of two primary components:

1. **Metadata Analysis Module**: Extracts metadata from a set of NEF files and identifies stable and variable fields. This information guides the creation of a synthetic flat.
2. **Synthetic Flat Generation Module**: Creates a flat frame in DNG format by manipulating Bayer-pattern pixel data directly. Star removal and smoothing techniques are configurable and modular.

The system emphasizes modularity, configurability, and extensibility, allowing for future enhancements without disrupting existing functionality.

---

## 3. Requirements

### Functional Requirements

1. **Metadata Extraction and Analysis**:
   - Extract all available metadata from NEF files.
   - Characterize the variability of each metadata field across all files.
   - Output a structured report (JSON or CSV) listing all metadata fields, the number of distinct values, and the values themselves.

2. **Synthetic Flat Frame Generation**:
   - Generate synthetic flat frames in DNG format, preserving compatibility with RawTherapee.
   - Process Bayer-pattern pixel data directly, without interpolation (demosaicing).
   - Apply star removal and smoothing techniques in a modular and configurable manner.
   - Allow users to select different star removal methods and provide parameters via configuration files.

3. **Configurability and Extensibility**:
   - Design the software to be modular, allowing easy addition of new star removal and smoothing methods.
   - Provide configuration files for specifying metadata to include in the DNG and processing parameters for different methods.

4. **Maintaining Metadata Consistency**:
   - Include necessary metadata in the synthetic flat DNG to ensure consistent processing with the NEF source files in RawTherapee.
   - Analyze metadata fields to identify stable and variable fields, and include critical fields in the DNG file.

### Non-Functional Requirements

1. **Performance**:
   - Efficiently process large batches of NEF files without significant delays.
   - Support multi-processing or parallel computation where appropriate.

2. **Modularity and Maintainability**:
   - Structure code in a modular fashion with clear separation of concerns.
   - Use design patterns where applicable to facilitate future extensions.

3. **Usability**:
   - Provide clear and informative error messages.
   - Allow users to configure processing via external configuration files.
   - Include detailed documentation and usage instructions.

4. **Portability**:
   - Ensure compatibility across major operating systems (Windows, Linux, macOS).
   - Avoid system-specific dependencies where possible.

---

## 4. Architecture

### High-Level Architecture

The system is divided into two main modules:

- **Metadata Analysis Module**: Responsible for extracting and analyzing metadata from NEF files.
- **Synthetic Flat Generation Module**: Processes pixel data from NEF files and generates the synthetic flat frame in DNG format.

### Directory Structure

```
project/
   apps/
      metadata_analysis/
         analyze_metadata.py
      flat_generation/
         create_flat.py
         starremoval/
            base.py        # Base class for star removal
            median_removal.py
            starnet_removal.py
            no_removal.py
         utils/
            dng_utils.py   # DNG creation and metadata utilities
            raw_utils.py   # NEF data extraction utilities
            filters.py     # Image processing utilities
      config/
         process_params.json    # Parameters for processing methods
         dng_metadata.json      # Metadata to include in DNG
   tests/
      test_metadata_analysis.py
      test_flat_generation.py
  docs/
    INITIAL_DESIGN.md
  LICENSE
  README.md
```

---

## 5. Module Details

### Metadata Analysis Module

**Purpose**: Extract and analyze metadata from NEF files to identify stable and variable fields.

#### Input

- `input_directory`: Directory containing NEF files.
- `output_file`: Path to save the metadata analysis report (JSON or CSV).

#### Output

- A structured file (JSON or CSV) containing:
  - List of all metadata fields.
  - For each field, the number of distinct values and the values themselves.

#### Workflow

1. **Enumerate NEF Files**:
   - Recursively scan the `input_directory` for NEF files.

2. **Extract Metadata**:
   - Use `pyexiv2` or call `exiftool` to extract metadata from each NEF file.

3. **Aggregate Metadata**:
   - Collect metadata fields and values from all files.
   - Store in a data structure (e.g., a dictionary) mapping fields to sets of values.

4. **Analyze Variability**:
   - For each metadata field, compute:
     - Number of distinct values (`distinct_count`).
     - List of values (`values`).

5. **Generate Report**:
   - Write the aggregated and analyzed metadata to the `output_file` in JSON or CSV format.

#### Example Output (JSON)

```json
{
  "Make": {
    "distinct_count": 1,
    "values": ["Nikon Corporation"]
  },
  "ISO": {
    "distinct_count": 2,
    "values": [400, 800]
  },
  "ExposureTime": {
    "distinct_count": 1,
    "values": ["30"]
  },
  "...": {
    "...": "...",
    "values": ["..."]
  }
}
```

### Synthetic Flat Generation Module

**Purpose**: Generate a synthetic flat frame by processing Bayer-pattern pixel data from NEF files and output it as a DNG file with appropriate metadata.

#### Input

- `input_directory`: Directory containing NEF files.
- `metadata_list_file`: JSON file specifying metadata fields to include in the DNG.
- `process_params_file`: JSON file with parameters for star removal and smoothing methods.
- `output_flat_dng`: Path to save the synthetic flat DNG file.

#### Output

- A DNG file containing the synthetic flat frame, compatible with RawTherapee.

#### Workflow

1. **Read NEF Files**:
   - Use `rawpy` to read raw pixel data from NEF files without applying demosaicing.

2. **Extract Bayer Channels**:
   - Identify the Bayer pattern (e.g., RGGB).
   - Extract pixel values corresponding to each channel (R, G, B) from the raw data.

3. **Process Channels Independently**:
   - For each channel:
     - Collect pixel data from all NEF files.
     - Apply star removal and smoothing techniques using the specified method and parameters.

4. **Reconstruct Bayer Pattern**:
   - Place the processed channels back into their respective positions in the Bayer pattern to reconstruct the flat frame.

5. **Create DNG File**:
   - Use utilities or libraries (e.g., `pydng`) to create a DNG file with the reconstructed Bayer data.
   - Inject necessary metadata into the DNG file using `pyexiv2` or `exiftool` based on `metadata_list_file`.

6. **Validate DNG File**:
   - Ensure the DNG file is properly formatted and compatible with RawTherapee.

---

## 6. Star Removal Framework

**Purpose**: Provide a modular and extensible framework for star removal and smoothing processes, allowing users to select different methods and configure parameters.

### Base Class

```python
class StarRemovalProcess:
    def apply(self, channel_image: np.ndarray, params: dict) -> np.ndarray:
        """
        Apply star removal and smoothing to the given image channel.

        Args:
            channel_image (np.ndarray): The input image channel.
            params (dict): Parameters for the star removal method.

        Returns:
            np.ndarray: The processed image channel.
        """
        pass  # To be implemented by subclasses
```

### Subclasses

1. **NoStarRemovalProcess**:
   - Does not perform any star removal; returns the original channel image.

2. **MedianFilterStarRemoval**:
   - Detects and masks stars based on a brightness threshold.
   - Applies median filtering to remove stars and smooth the image.

3. **StarNetRemovalProcess**:
   - Utilizes external tool **StarNet++** to remove stars.
   - Requires the path to the StarNet++ executable.
   - May need to convert the channel image to a compatible format (e.g., TIFF).

### Example Configuration (`process_params.json`)

```json
{
  "method": "starnet",
  "starnet_executable_path": "/usr/local/bin/StarNet++",
  "gaussian_blur_sigma": 2.0,
  "threshold": 0.1
}
```

### Dynamic Method Selection

- The software reads the `method` field from `process_params.json`.
- Instantiates the corresponding subclass of `StarRemovalProcess`.
- Applies the `apply` method to each image channel using provided parameters.

---

## 7. Configuration Files

### Metadata List File

Defines the metadata fields to include in the DNG.

**Format**: JSON

**Example (`dng_metadata.json`)**:

```json
{
  "Make": "Nikon Corporation",
  "Model": "NIKON D5300",
  "CFA Pattern": "RGGB",
  "AsShotNeutral": [0.5, 1.0, 0.5],
  "BlackLevel": 600,
  "WhiteLevel": 16383,
  "ColorMatrix1": [
    [0.679, -0.148, -0.073],
    [-0.329, 1.089, 0.256],
    [-0.013, 0.203, 0.738]
  ],
  "...": "..."
}
```

### Process Parameters File

Defines the parameters for star removal and smoothing.

**Format**: JSON

**Example (`process_params.json`)**:

```json
{
  "method": "median",
  "threshold": 0.1,
  "median_filter_size": 3,
  "gaussian_blur_sigma": 2.0
}
```

---

## 8. Implementation Guidelines

### Libraries and Dependencies

- **Python Version**: Python 3.x

- **Recommended Libraries**:

  - `rawpy`: For reading NEF RAW data and accessing the Bayer pattern.
    - **Usage**: Extract raw pixel data directly from NEF files without demosaicing.
  - `numpy`, `scipy` (`scipy.ndimage`): For numerical computations and image processing.
    - **Usage**: Manipulate arrays, apply median and Gaussian filters for smoothing.
  - `pyexiv2` or `exiftool` (via `subprocess`): For metadata extraction and modification.
    - **Usage**: Read and write EXIF metadata, inject necessary fields into DNG files.
  - `pydng`: For creating DNG files from raw Bayer data.
    - **Usage**: Generate DNG files with the reconstructed Bayer data.
  - `json`, `csv`: For structured data handling.
    - **Usage**: Parse configuration files (`process_params.json`, `dng_metadata.json`) and metadata lists.
  - `subprocess`: For invoking external tools like StarNet++.
    - **Usage**: Run external executables for star removal processes.
  - `os`, `glob`: For file system operations.
    - **Usage**: Enumerate NEF files in directories, handle file paths.

### Data Formats

- **Metadata Analysis Output**: The metadata analysis file should be in a structured format such as JSON or CSV.
  - **JSON**: Preferred for its flexibility with nested data structures.
  - **CSV**: Suitable for simple tabular data.

- **Configuration Files**: Parameters for processing methods should be provided via JSON files.
  - `dng_metadata.json`: Specifies metadata fields to include in the DNG file.
  - `process_params.json`: Defines parameters for star removal and smoothing methods.

### Modularity and Extensibility

- **Star Removal Framework**:

  - Implement a base class `StarRemovalProcess` that defines the interface for star removal methods.

    ```python
    class StarRemovalProcess:
        def apply(self, channel_image: np.ndarray, params: dict) -> np.ndarray:
            """Apply star removal and smoothing to the given image channel."""
            pass  # To be implemented by subclasses
    ```

  - **Subclasses**:

    - `NoStarRemovalProcess`: Performs no star removal; returns the original image.
    - `MedianFilterStarRemoval`: Uses thresholding and median filtering to remove stars.
    - `StarNetRemovalProcess`: Utilizes the external tool StarNet++ for star removal.
      - **Requires**: Path to the StarNet++ executable provided in the processing parameters file.
      - **Usage**: Calls StarNet++ via `subprocess` and processes the output accordingly.

- **Configuration of Processing Parameters**:

  - Use a JSON file (`process_params.json`) to specify the method and parameters for star removal and smoothing.

    ```json
    {
      "method": "starnet",
      "starnet_executable_path": "/usr/local/bin/StarNet++",
      "gaussian_blur_sigma": 2.0,
      "threshold": 0.1
    }
    ```

  - **Parameters**:

    - `method`: The star removal method to use (e.g., `"median"`, `"starnet"`).
    - Additional parameters specific to each method (e.g., `starnet_executable_path`, `gaussian_blur_sigma`).

  - **Extendibility**:

    - New methods can be added by creating new subclasses of `StarRemovalProcess` and updating `process_params.json` accordingly.

### Implementation Steps

1. **Metadata Analysis Module**:

   - **Enumerate NEF Files**: Use `os` and `glob` to list all NEF files in the input directory.

   - **Extract Metadata**:

     - Use `pyexiv2` or call `exiftool` via `subprocess` to extract metadata from each NEF file.
     - Collect metadata into a dictionary mapping metadata fields to sets of values.

   - **Analyze Variability**:

     - For each metadata field, compute the number of distinct values and list them.
     - Identify stable and variable fields across all NEF files.

   - **Output Results**:

     - Write the analysis to a structured JSON or CSV file (`metadata_analysis.json`).
     - Example output:

       ```json
       {
         "Make": {
           "distinct_count": 1,
           "values": ["Nikon Corporation"]
         },
         "ISO": {
           "distinct_count": 2,
           "values": [400, 800]
         }
       }
       ```

2. **Synthetic Flat Generation Module**:

   - **Data Extraction**:

     - Use `rawpy` to read raw Bayer data from NEF files without applying demosaicing.
     - Identify the Bayer pattern (e.g., `RGGB`) and extract pixel data corresponding to each channel (R, G, B).

   - **Process Channels Independently**:

     - **Collect Channel Data**: For each color channel, collect data from all images.
     - **Star Removal and Smoothing**:

       - Instantiate the appropriate subclass of `StarRemovalProcess` based on `process_params.json`.
       - Apply the `apply` method to each image channel with the specified parameters.

       ```python
       # Example of dynamic method selection
       method = process_params["method"]
       if method == "median":
           processor = MedianFilterStarRemoval()
       elif method == "starnet":
           processor = StarNetRemovalProcess()
       else:
           processor = NoStarRemovalProcess()
       ```

   - **Reconstruct Bayer Pattern**:

     - Reassemble the processed channels back into the original Bayer pattern.
     - Combine the channels to form the final flat frame data.

   - **Create DNG File**:

     - Use `pydng` or similar libraries to create a DNG file with the reconstructed Bayer data.
     - Inject necessary metadata into the DNG file using `pyexiv2` or `exiftool` based on `dng_metadata.json`.

     ```json
     {
       "Make": "Nikon Corporation",
       "Model": "NIKON D5300",
       "CFA Pattern": "RGGB",
       "AsShotNeutral": [0.5, 1.0, 0.5],
       "BlackLevel": 600,
       "WhiteLevel": 16383
     }
     ```

### Error Handling and Logging

- **Input Validation**:

  - Verify that input directories and files exist and are accessible.
  - Check the correctness and completeness of JSON configuration files.
  - Ensure required parameters are provided for the selected methods.

- **Error Messages**:

  - Provide clear and descriptive messages indicating the nature of errors.
  - Suggest possible solutions or corrective actions.

- **Logging**:

  - Use Python's `logging` module to record the processing steps and any issues encountered.
  - Include timestamps, logging levels (INFO, WARNING, ERROR), and contextual information.

### Testing

- **Unit Tests**:

  - Test individual functions and classes, including different star removal methods.
  - Use mock data and files to simulate various scenarios.

- **Integration Tests**:

  - Test the complete workflow with a set of sample NEF files.
  - Verify that the generated DNG file is correctly formatted and compatible with RawTherapee.

### Future Extensions

- **Adding New Star Removal Methods**:

  - Developers can add new subclasses of `StarRemovalProcess` for additional star removal techniques.
  - Update `process_params.json` to include parameters for the new method.

- **Enhanced Configuration**:

  - Expand the parameters in `process_params.json` to provide more control over processing options.
  - Allow users to specify additional processing steps or adjust existing ones.

- **Support for Other RAW Formats**:

  - Extend the software to handle other RAW formats (e.g., CR2, ARW) by adjusting the data extraction functions.

---

## 9. Future Extensions

1. **Support for Additional RAW Formats**:
   - Extend compatibility to other RAW formats like CR2 (Canon) or ARW (Sony).

2. **Advanced Star Removal Techniques**:
   - Implement more sophisticated algorithms for star detection and removal.

3. **GPU Acceleration**:
   - Utilize GPU processing for handling large datasets more efficiently.

4. **Graphical User Interface (GUI)**:
   - Develop a user-friendly GUI for easier configuration and usage.

5. **Batch Processing Enhancements**:
   - Implement more robust batch processing capabilities and progress tracking.

6. **Plugin System**:
   - Allow third-party developers to add custom star removal or smoothing methods.

---




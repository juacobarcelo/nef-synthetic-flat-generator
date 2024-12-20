# Flat Synthetic Generation Tool

## This is a work in progress. This repo does not have runnable code yet.

## Overview
This project provides a two-part tool to process NEF (Nikon RAW) files for astrophotography, enabling the generation of synthetic flat frames in DNG format that are consistent with the pipeline used in RawTherapee. The tool also includes functionality to analyze metadata from NEF files, allowing for informed inclusion of metadata in the synthetic flat.

The software is divided into two main components:

1. **Metadata Analysis**: Extracts and characterizes metadata variability across NEF files in a directory.
2. **Synthetic Flat Generation**: Creates a flat frame in DNG format from NEF files, using advanced star removal and smoothing techniques.

---

## Features
- Analyze and categorize metadata from NEF files, identifying stable and variable fields.
- Generate a flat frame using pixel-level manipulation of Bayer data without demosaicing.
- Modular and extensible framework for star removal and smoothing.
- Support for external tools like StarNet++ for star removal.
- Highly configurable via JSON parameter files.

---

## Requirements

### Python Libraries
- `rawpy`: For reading NEF RAW data.
- `exiftool` or `pyexiv2`: For metadata extraction and modification.
- `numpy` and `scipy`: For array manipulation and image processing.
- `pydng` (optional): For DNG creation, or alternatively, use `exiftool` for metadata injection.
- `json`, `csv`: For structured data handling.

### Optional Tools
- **StarNet++**: External tool for star removal. If not available on your system, you must install it.

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/flat-synthetic-generator.git
   cd flat-synthetic-generator
   ```

2. Install required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure `exiftool` and optional external tools like StarNet++ are installed and available in your system PATH.

4. Install StarNet++:

   - If StarNet++ is not available on your system, you must install it. In the `3erd_party_software` directory, there is a `StarNetv2CLI` directory containing the decompressed download of StarNet++ from the following URL: [StarNetv2CLI_linux.zip](https://starnetastro.com/wp-content/uploads/2022/03/StarNetv2CLI_linux.zip).
   - Ensure the StarNet++ executable is available in your system PATH or specify the path in the processing parameters file.

---

## Usage

### 1. Metadata Analysis
Analyze NEF files to extract metadata and identify variability across files.

**Command:**
```bash
python analyze_metadata.py --input_directory /path/to/nef_lights --output_file /path/to/metadata_analysis.json
```

**Parameters:**
- `--input_directory`: Directory containing NEF files.
- `--output_file`: Path to the output JSON file summarizing metadata analysis.

**Output:**
- A structured JSON file (or CSV) with metadata fields, distinct values, and variability.

**Example JSON Output:**
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

### 2. Synthetic Flat Generation
Generate a synthetic flat in DNG format from NEF files.

**Command:**
```bash
python create_flat.py \
    --input_directory /path/to/nef_lights \
    --metadata_list_file /path/to/dng_metadata.json \
    --process_params_file /path/to/process_params.json \
    --output_flat_dng /path/to/flat_synthetic.dng
```

**Parameters:**
- `--input_directory`: Directory containing NEF files.
- `--metadata_list_file`: Path to the JSON file specifying metadata to include in the DNG.
- `--process_params_file`: Path to the JSON file defining star removal and smoothing parameters.
- `--output_flat_dng`: Path to save the generated DNG file.

**Example `dng_metadata.json`:**
```json
{
  "Make": "Nikon Corporation",
  "Model": "NIKON D5300",
  "CFA Pattern": "RGGB",
  "AsShotNeutral": [0.5, 1.0, 0.5]
}
```

**Example `process_params.json`:**
```json
{
  "method": "starnet",
  "starnet_executable_path": "/usr/local/bin/StarNet++",
  "gaussian_blur_sigma": 2.0
}
```

---

## Architecture

### Project Structure
```
project/
  metadata_analysis/
    analyze_metadata.py
  flat_generation/
    create_flat.py
    starremoval/
      base.py        # Base class for star removal strategies
      median_removal.py
      starnet_removal.py
    utils/
      dng_utils.py   # DNG creation and editing utilities
      raw_utils.py   # RAW/Bayer data manipulation utilities
      filters.py     # Median and Gaussian blur filters
```

### Star Removal Framework
- **Base Class:** `StarRemovalProcess`
  ```python
  class StarRemovalProcess:
      def apply(self, channel_image: np.ndarray, params: dict) -> np.ndarray:
          pass  # To be implemented by subclasses
  ```

- **Subclasses:**
  - `MedianFilterStarRemoval`: Uses thresholding and median filtering.
  - `StarNetRemovalProcess`: Calls StarNet++ for star removal.

### Example `process_params.json`
```json
{
  "method": "median",
  "threshold": 0.1,
  "gaussian_blur_sigma": 2.0
}
```

---

## Examples

### 1. Analyze Metadata
```bash
python analyze_metadata.py \
    --input_directory /path/to/nef_lights \
    --output_file /path/to/results/metadata_analysis.json
```

### 2. Create Synthetic Flat
```bash
python create_flat.py \
    --input_directory /path/to/nef_lights \
    --metadata_list_file /path/to/dng_metadata.json \
    --process_params_file /path/to/process_params.json \
    --output_flat_dng /path/to/flat_synthetic.dng
```

---

## Development Environment

Este proyecto se desarrolla en un contenedor de Visual Studio Code (vscode), lo que facilita la configuración del entorno y las dependencias.

---

## Future Extensions
- Add support for other external tools for star removal.
- Incorporate advanced metadata validation and auto-correction.
- Implement additional smoothing and star removal strategies.

---

## License
This project is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).

You are free to:
- **Share**: Copy and redistribute the material in any medium or format.
- **Adapt**: Remix, transform, and build upon the material.

Under the following terms:
- **Attribution**: You must give appropriate credit, provide a link to the license, and indicate if changes were made.
- **NonCommercial**: You may not use the material for commercial purposes.

For more details, see the [LICENSE](./LICENSE) file.


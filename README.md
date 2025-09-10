# Image Size Reducer

A Python algorithm that automatically reduces image file sizes to meet specified maximum file size requirements. The tool intelligently adjusts image quality and dimensions to achieve the target file size while maintaining the best possible visual quality.

## Features

- 🎯 **Target File Size**: Specify maximum file size in MB
- 🔄 **Smart Reduction**: Uses quality reduction first, then resizing if needed
- 📁 **Batch Processing**: Process multiple images at once
- 🖼️ **Format Support**: JPG, PNG, BMP, TIFF, WebP input formats
- 📊 **Detailed Reports**: Get reduction statistics and processing info
- 🎨 **Quality Preservation**: Maintains best possible quality within size constraints

## Installation

1. Install Python 3.7 or higher
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from image_reducer import ImageSizeReducer

# Create reducer with 1MB max file size
reducer = ImageSizeReducer(max_file_size_mb=1.0)

# Reduce a single image
result = reducer.reduce_image_size(
    input_path="large_image.jpg",
    output_path="reduced_image.jpg"
)

print(f"Reduced from {result['original_size_mb']:.2f}MB to {result['final_size_mb']:.2f}MB")
```

### Batch Processing

```python
# Process all images in a folder
results = reducer.reduce_multiple_images(
    input_folder="input_images",
    output_folder="output_images"
)
```

## How It Works

The algorithm uses a two-step approach:

1. **Quality Reduction**: Starts with 95% quality and reduces by 5% increments until the target size is met
2. **Dimension Scaling**: If quality reduction isn't sufficient, it scales down the image dimensions by 10% increments

This approach ensures the best possible visual quality while meeting your file size requirements.

## Examples

Run the example script to see the reducer in action:

```bash
python example_usage.py
```

### Different Size Limits

```python
# Very small files (200KB)
small_reducer = ImageSizeReducer(max_file_size_mb=0.2)

# Medium files (1MB)
medium_reducer = ImageSizeReducer(max_file_size_mb=1.0)

# Large files (5MB)
large_reducer = ImageSizeReducer(max_file_size_mb=5.0)
```

## API Reference

### ImageSizeReducer Class

#### Constructor
```python
ImageSizeReducer(max_file_size_mb=1.0)
```
- `max_file_size_mb`: Maximum file size in megabytes (default: 1.0)

#### Methods

##### reduce_image_size(input_path, output_path=None)
Reduces a single image to meet the size requirement.

**Parameters:**
- `input_path` (str): Path to the input image
- `output_path` (str, optional): Path to save the reduced image

**Returns:**
Dictionary with reduction details:
```python
{
    'original_size_mb': 2.5,
    'final_size_mb': 0.98,
    'reduction_percentage': 60.8,
    'quality_used': 75,
    'scale_factor': 0.9,
    'original_dimensions': (1920, 1080),
    'final_dimensions': (1728, 972),
    'message': 'Image successfully reduced'
}
```

##### reduce_multiple_images(input_folder, output_folder=None)
Processes multiple images in a folder.

**Parameters:**
- `input_folder` (str): Path to folder containing images
- `output_folder` (str, optional): Path to save reduced images

**Returns:**
List of results for each processed image.

## Supported Formats

- **Input**: JPG, JPEG, PNG, BMP, TIFF, WebP
- **Output**: JPEG (for consistency and optimal compression)

## Tips for Best Results

1. **Start with high-quality originals** for better results
2. **Use reasonable size limits** - very small limits may heavily impact quality
3. **JPEG format** is used for output as it provides the best size/quality ratio
4. **Transparent images** are converted with a white background
5. **Batch processing** is more efficient for multiple images

## Examples Directory Structure

```
image_size_reducer/
├── image_reducer.py          # Main algorithm
├── example_usage.py         # Usage examples
├── requirements.txt         # Dependencies
├── README.md               # This file
├── input_images/           # Put your images here (create this folder)
└── output_images/          # Reduced images will be saved here
```

## Error Handling

The reducer handles common issues gracefully:
- Missing input files
- Unsupported formats
- Corrupted images
- Permission errors

## License

This project is open source and available under the MIT License.

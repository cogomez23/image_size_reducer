"""
Image Size Reducer Algorithm
Reduces image file size to a specified maximum size through quality and dimension adjustments.
"""

import os
from PIL import Image
import io


class ImageSizeReducer:
    def __init__(self, max_file_size_mb=1.0):
        """
        Initialize the image reducer.
        
        Args:
            max_file_size_mb (float): Maximum file size in megabytes
        """
        self.max_file_size_bytes = int(max_file_size_mb * 1024 * 1024)
        
    def get_file_size(self, image_data):
        """Get the size of image data in bytes."""
        return len(image_data)
    
    def reduce_quality(self, image, quality):
        """Reduce image quality and return the compressed data."""
        output = io.BytesIO()
        # Convert RGBA to RGB if necessary for JPEG
        if image.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            image = background
        
        image.save(output, format='JPEG', quality=quality, optimize=True)
        return output.getvalue()
    
    def resize_image(self, image, scale_factor):
        """Resize image by a scale factor."""
        new_width = int(image.width * scale_factor)
        new_height = int(image.height * scale_factor)
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def reduce_image_size(self, input_path, output_path=None):
        """
        Reduce image size to meet the maximum file size requirement.
        
        Args:
            input_path (str): Path to the input image
            output_path (str): Path to save the reduced image (optional)
            
        Returns:
            dict: Information about the reduction process
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Open the original image
        with Image.open(input_path) as original_image:
            original_size = os.path.getsize(input_path)
            
            # If already under the limit, just copy
            if original_size <= self.max_file_size_bytes:
                if output_path:
                    original_image.save(output_path, optimize=True)
                return {
                    'original_size_mb': original_size / (1024 * 1024),
                    'final_size_mb': original_size / (1024 * 1024),
                    'reduction_percentage': 0,
                    'quality_used': 100,
                    'scale_factor': 1.0,
                    'message': 'Image already under size limit'
                }
            
            current_image = original_image.copy()
            quality = 95
            scale_factor = 1.0
            
            # First, try reducing quality
            while quality >= 10:
                compressed_data = self.reduce_quality(current_image, quality)
                current_size = self.get_file_size(compressed_data)
                
                if current_size <= self.max_file_size_bytes:
                    break
                
                quality -= 5
            
            # If quality reduction isn't enough, start resizing
            if current_size > self.max_file_size_bytes:
                scale_step = 0.9
                
                while scale_factor > 0.1 and current_size > self.max_file_size_bytes:
                    scale_factor *= scale_step
                    resized_image = self.resize_image(original_image, scale_factor)
                    
                    # Try different qualities for the resized image
                    test_quality = 95
                    while test_quality >= 10:
                        compressed_data = self.reduce_quality(resized_image, test_quality)
                        current_size = self.get_file_size(compressed_data)
                        
                        if current_size <= self.max_file_size_bytes:
                            current_image = resized_image
                            quality = test_quality
                            break
                        
                        test_quality -= 5
                    
                    if current_size <= self.max_file_size_bytes:
                        break
            
            # Save the final image
            final_data = self.reduce_quality(current_image, quality)
            final_size = self.get_file_size(final_data)
            
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(final_data)
            
            reduction_percentage = ((original_size - final_size) / original_size) * 100
            
            return {
                'original_size_mb': original_size / (1024 * 1024),
                'final_size_mb': final_size / (1024 * 1024),
                'reduction_percentage': reduction_percentage,
                'quality_used': quality,
                'scale_factor': scale_factor,
                'original_dimensions': (original_image.width, original_image.height),
                'final_dimensions': (current_image.width, current_image.height),
                'message': 'Image successfully reduced'
            }
    
    def reduce_multiple_images(self, input_folder, output_folder=None):
        """
        Reduce multiple images in a folder.
        
        Args:
            input_folder (str): Path to folder containing images
            output_folder (str): Path to save reduced images (optional)
            
        Returns:
            list: Results for each processed image
        """
        if not os.path.exists(input_folder):
            raise FileNotFoundError(f"Input folder not found: {input_folder}")
        
        if output_folder and not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp')
        results = []
        
        for filename in os.listdir(input_folder):
            if filename.lower().endswith(supported_formats):
                input_path = os.path.join(input_folder, filename)
                output_path = None
                
                if output_folder:
                    # Change extension to .jpg for consistency
                    name_without_ext = os.path.splitext(filename)[0]
                    output_path = os.path.join(output_folder, f"{name_without_ext}_reduced.jpg")
                
                try:
                    result = self.reduce_image_size(input_path, output_path)
                    result['filename'] = filename
                    results.append(result)
                    print(f"✓ Processed {filename}: {result['original_size_mb']:.2f}MB → {result['final_size_mb']:.2f}MB ({result['reduction_percentage']:.1f}% reduction)")
                except Exception as e:
                    print(f"✗ Error processing {filename}: {str(e)}")
                    results.append({
                        'filename': filename,
                        'error': str(e)
                    })
        
        return results


def main():
    """Example usage of the ImageSizeReducer."""
    # Create reducer with 1MB max file size
    reducer = ImageSizeReducer(max_file_size_mb=1.0)
    
    # Example: Reduce a single image
    try:
        result = reducer.reduce_image_size(
            input_path="input_image.jpg",
            output_path="reduced_image.jpg"
        )
        print("Single image reduction result:")
        print(f"Original: {result['original_size_mb']:.2f}MB")
        print(f"Final: {result['final_size_mb']:.2f}MB")
        print(f"Reduction: {result['reduction_percentage']:.1f}%")
        print(f"Quality: {result['quality_used']}")
        print(f"Scale: {result['scale_factor']:.2f}")
    except FileNotFoundError:
        print("Example image not found. Please provide your own image path.")
    
    # Example: Process multiple images
    # results = reducer.reduce_multiple_images("input_folder", "output_folder")


if __name__ == "__main__":
    main()

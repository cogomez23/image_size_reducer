#!/usr/bin/env python3
"""
Example usage of the Image Size Reducer
This script demonstrates how to use the ImageSizeReducer class.
"""

from image_reducer import ImageSizeReducer
import os


def example_single_image():
    """Example: Reduce a single image to 500KB."""
    print("=== Single Image Reduction Example ===")
    
    # Create reducer with 0.5MB (500KB) max file size
    reducer = ImageSizeReducer(max_file_size_mb=0.5)
    
    # Replace with your actual image path
    input_image = "sample_image.jpg"  # Put your image here
    output_image = "reduced_sample.jpg"
    
    if not os.path.exists(input_image):
        print(f"⚠️  Please place an image named '{input_image}' in this directory to test.")
        print("   Or modify the 'input_image' variable to point to your image.")
        return
    
    try:
        result = reducer.reduce_image_size(input_image, output_image)
        
        print(f"✅ Success! Image reduced:")
        print(f"   📁 Original size: {result['original_size_mb']:.2f} MB")
        print(f"   📁 Final size: {result['final_size_mb']:.2f} MB")
        print(f"   📉 Reduction: {result['reduction_percentage']:.1f}%")
        print(f"   🎨 Quality used: {result['quality_used']}%")
        print(f"   📏 Scale factor: {result['scale_factor']:.2f}")
        print(f"   🖼️  Original dimensions: {result['original_dimensions']}")
        print(f"   🖼️  Final dimensions: {result['final_dimensions']}")
        print(f"   💾 Saved as: {output_image}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_batch_processing():
    """Example: Process multiple images in a folder."""
    print("\n=== Batch Processing Example ===")
    
    # Create reducer with 1MB max file size
    reducer = ImageSizeReducer(max_file_size_mb=1.0)
    
    input_folder = "input_images"
    output_folder = "output_images"
    
    if not os.path.exists(input_folder):
        print(f"⚠️  Please create a folder named '{input_folder}' and add some images to test batch processing.")
        return
    
    try:
        results = reducer.reduce_multiple_images(input_folder, output_folder)
        
        print(f"✅ Batch processing complete!")
        print(f"   📂 Processed {len(results)} files")
        
        total_original = sum(r.get('original_size_mb', 0) for r in results if 'original_size_mb' in r)
        total_final = sum(r.get('final_size_mb', 0) for r in results if 'final_size_mb' in r)
        
        if total_original > 0:
            total_reduction = ((total_original - total_final) / total_original) * 100
            print(f"   📊 Total original size: {total_original:.2f} MB")
            print(f"   📊 Total final size: {total_final:.2f} MB")
            print(f"   📊 Total reduction: {total_reduction:.1f}%")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_different_sizes():
    """Example: Show different max file sizes."""
    print("\n=== Different Size Limits Example ===")
    
    input_image = "sample_image.jpg"
    
    if not os.path.exists(input_image):
        print(f"⚠️  Please place an image named '{input_image}' in this directory to test.")
        return
    
    # Test different size limits
    size_limits = [2.0, 1.0, 0.5, 0.2]  # MB
    
    for size_limit in size_limits:
        reducer = ImageSizeReducer(max_file_size_mb=size_limit)
        output_name = f"reduced_{size_limit}MB.jpg"
        
        try:
            result = reducer.reduce_image_size(input_image, output_name)
            print(f"📏 {size_limit}MB limit: {result['final_size_mb']:.2f}MB "
                  f"(Quality: {result['quality_used']}%, Scale: {result['scale_factor']:.2f})")
        except Exception as e:
            print(f"❌ Error with {size_limit}MB limit: {e}")


def main():
    """Run all examples."""
    print("🖼️  Image Size Reducer - Example Usage\n")
    
    # Run examples
    example_single_image()
    example_batch_processing()
    example_different_sizes()
    
    print("\n" + "="*50)
    print("💡 Tips:")
    print("   • Supported formats: JPG, PNG, BMP, TIFF, WebP")
    print("   • Output is always saved as JPEG for consistency")
    print("   • The algorithm tries quality reduction first, then resizing")
    print("   • Transparent images get a white background")
    print("   • Very small size limits may significantly reduce quality")


if __name__ == "__main__":
    main()

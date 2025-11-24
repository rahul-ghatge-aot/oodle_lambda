#!/usr/bin/env python3
"""
Local Image Enhancement Script
Enhances images from the 'images' folder using Real-ESRGAN and saves to 'enhanced' folder
"""

import os
import sys
from PIL import Image
import glob
import tempfile
import numpy as np

# Try to import Real-ESRGAN components
REALESRGAN_AVAILABLE = False
try:
    from realesrgan import RealESRGANer
    from realesrgan.archs.srvgg_arch import SRVGGNetCompact
    from basicsr.utils.download_util import load_file_from_url
    REALESRGAN_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Real-ESRGAN dependencies not available ({e}). Using fallback method.")

def enhance_image(image_path, model, scale):
    """
    Enhances an image using the Real-ESRGAN model.
    """
    try:
        img = Image.open(image_path).convert("RGB")
        img_np = np.array(img)
        enhancer = RealESRGANer(
            scale=scale,
            model_path=model,
            dni_weight=None,
            model=SRVGGNetCompact(num_in_ch=3, num_out_ch=3, num_feat=64, num_conv=32, upscale=4, act_type='prelu'),
            tile=0,
            tile_pad=10,
            pre_pad=0,
            half=False,
            gpu_id=None,
        )
        upsampled_img_np, _ = enhancer.enhance(img_np, outscale=scale)
        upsampled_img = Image.fromarray(upsampled_img_np)
        return upsampled_img
    except Exception as e:
        print(f"Error enhancing image with Real-ESRGAN: {e}")
        print("Falling back to PIL interpolation...")
        try:
            img = Image.open(image_path).convert("RGB")
            orig_w, orig_h = img.size
            new_w, new_h = orig_w * scale, orig_h * scale
            return img.resize((new_w, new_h), Image.LANCZOS)
        except Exception as e2:
            print(f"PIL fallback also failed: {e2}")
            return None

def main():
    # Check if images folder exists
    if not os.path.exists('images'):
        print("Error: 'images' folder not found. Please create it and add some images.")
        sys.exit(1)

    # Create enhanced folder if it doesn't exist
    os.makedirs('enhanced', exist_ok=True)

    # Supported image formats
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.webp']

    # Find all images in the images folder
    image_files = []
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join('images', ext)))

    if not image_files:
        print("No image files found in 'images' folder.")
        print("Supported formats: JPG, PNG, BMP, TIFF, WebP")
        sys.exit(1)

    print(f"Found {len(image_files)} image(s) to enhance.")

    # Load the Real-ESRGAN model
    model_path = None
    realesrgan_working = False
    if REALESRGAN_AVAILABLE:
        print("Loading Real-ESRGAN model...")
        try:
            model_path = load_file_from_url(url='https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth',
                                            model_dir=tempfile.gettempdir() + '/realesrgan', progress=True)
            print("Real-ESRGAN model loaded successfully.")
            realesrgan_working = True
        except Exception as e:
            print(f"Error loading Real-ESRGAN model: {e}")
            print("Falling back to PIL interpolation...")
    else:
        print("Real-ESRGAN not available, using PIL interpolation.")

    # Process each image
    scale = 4  # You can change this scale factor
    processed = 0

    for image_path in image_files:
        filename = os.path.basename(image_path)
        name, ext = os.path.splitext(filename)

        print(f"Processing: {filename}")

        # Get original image size
        with Image.open(image_path) as img:
            orig_w, orig_h = img.size
        new_w, new_h = orig_w * scale, orig_h * scale

        if model_path and realesrgan_working:
            # Use Real-ESRGAN
            enhanced_img = enhance_image(image_path, model_path, scale)
        else:
            # Use PIL interpolation
            print("  Using PIL interpolation")
            try:
                img = Image.open(image_path).convert("RGB")
                enhanced_img = img.resize((new_w, new_h), Image.LANCZOS)
            except Exception as e:
                print(f"  PIL processing failed: {e}")
                enhanced_img = None

        if enhanced_img:
            # Save the enhanced image
            output_filename = f"{name}_x{scale}{ext}"
            output_path = os.path.join('enhanced', output_filename)
            enhanced_img.save(output_path, quality=95)  # High quality JPEG

            method = "Real-ESRGAN" if model_path and realesrgan_working else "PIL Lanczos"
            print(f"  Enhanced: {orig_w}x{orig_h} -> {new_w}x{new_h} ({method})")
            print(f"  Saved to: {output_path}")
            processed += 1
        else:
            print(f"  Failed to enhance: {filename}")

    print(f"\nSuccessfully enhanced {processed} out of {len(image_files)} images.")
    method = "Real-ESRGAN" if (model_path and realesrgan_working) else "PIL interpolation"
    print(f"Enhanced images saved to 'enhanced' folder with {scale}x scaling using {method}.")

if __name__ == "__main__":
    main()

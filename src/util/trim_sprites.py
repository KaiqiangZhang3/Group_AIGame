#!/usr/bin/env python3
"""
Sprite Trimmer - Removes excess transparent pixels around sprite images.

This script analyzes all sprite images in the Assets/Sprites directory,
detects the actual content boundaries (removing transparent pixels),
and saves trimmed versions while maintaining folder structure.
"""

import os
import sys
from PIL import Image
import shutil

def get_trim_boundaries(img):
    """Find the boundaries of non-transparent content in an image."""
    # Get the alpha channel
    if img.mode != 'RGBA':
        return None  # Only process RGBA images

    # Get image dimensions
    width, height = img.size
    
    # Find content boundaries (left, top, right, bottom)
    left, top, right, bottom = width, height, 0, 0
    
    # Get alpha data
    alpha_data = img.getchannel('A').getdata()
    
    # Scan for non-transparent pixels
    for y in range(height):
        for x in range(width):
            # Get alpha value at this pixel
            alpha = alpha_data[y * width + x]
            if alpha > 0:  # Non-transparent pixel
                left = min(left, x)
                top = min(top, y)
                right = max(right, x)
                bottom = max(bottom, y)
    
    # Return None if image is fully transparent
    if left >= right or top >= bottom:
        return None
    
    # Add a small padding (1-2 pixels) if desired
    padding = 0
    left = max(0, left - padding)
    top = max(0, top - padding)
    right = min(width - 1, right + padding)
    bottom = min(height - 1, bottom + padding)
    
    return (left, top, right + 1, bottom + 1)  # +1 because crop is exclusive on right/bottom

def process_sprite_folder(src_dir, dest_dir, adjust_bottom=True):
    """Process all sprite images in a folder and its subfolders."""
    
    # Create destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)
    
    # Find the maximum bottom edge value across all images in this animation
    # This helps ensure consistent vertical alignment
    max_bottom = 0
    consistent_bottom = {}
    
    # First pass - determine consistent bottom if adjust_bottom is True
    if adjust_bottom:
        for anim_folder in os.listdir(src_dir):
            anim_path = os.path.join(src_dir, anim_folder)
            if os.path.isdir(anim_path):
                folder_bottom = 0
                folder_images = []
                
                for filename in sorted(os.listdir(anim_path)):
                    if filename.lower().endswith('.png'):
                        img_path = os.path.join(anim_path, filename)
                        try:
                            with Image.open(img_path) as img:
                                # Get trim boundaries
                                bounds = get_trim_boundaries(img)
                                if bounds:
                                    folder_images.append(img_path)
                                    _, _, _, bottom = bounds
                                    folder_bottom = max(folder_bottom, bottom)
                        except Exception as e:
                            print(f"Error processing {img_path}: {e}")
                
                if folder_images:
                    for img_path in folder_images:
                        consistent_bottom[img_path] = folder_bottom
    
    # Total stats
    processed = 0
    skipped = 0
    errors = 0
    
    # Process all folders
    for anim_folder in os.listdir(src_dir):
        anim_path = os.path.join(src_dir, anim_folder)
        if os.path.isdir(anim_path):
            # Create destination animation folder
            dest_anim_path = os.path.join(dest_dir, anim_folder)
            os.makedirs(dest_anim_path, exist_ok=True)
            
            print(f"Processing folder: {anim_folder}")
            
            # Process all PNG files in this animation folder
            for filename in sorted(os.listdir(anim_path)):
                if filename.lower().endswith('.png'):
                    img_path = os.path.join(anim_path, filename)
                    dest_img_path = os.path.join(dest_anim_path, filename)
                    
                    try:
                        with Image.open(img_path) as img:
                            # Get trim boundaries
                            bounds = get_trim_boundaries(img)
                            
                            if bounds:
                                left, top, right, bottom = bounds
                                
                                # Adjust bottom to be consistent with other frames in this animation
                                if img_path in consistent_bottom:
                                    bottom = consistent_bottom[img_path]
                                
                                # Crop the image
                                cropped = img.crop((left, top, right, bottom))
                                
                                # Save the cropped image
                                cropped.save(dest_img_path)
                                processed += 1
                                print(f"  ✓ Trimmed: {filename} from {img.size} to {cropped.size}")
                            else:
                                # Just copy the original if no trim needed
                                shutil.copy(img_path, dest_img_path)
                                skipped += 1
                                print(f"  - Skipped: {filename} (no trim needed)")
                    
                    except Exception as e:
                        print(f"  ✗ Error processing {img_path}: {e}")
                        errors += 1
                        # Copy original on error
                        try:
                            shutil.copy(img_path, dest_img_path)
                        except:
                            pass
    
    return processed, skipped, errors

if __name__ == "__main__":
    # Define source and destination directories
    src_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                          "Assets", "Sprites")
    dest_dir = os.path.join(os.path.dirname(src_dir), "Sprites_Trimmed")
    
    print(f"Source directory: {src_dir}")
    print(f"Destination directory: {dest_dir}")
    
    if not os.path.exists(src_dir):
        print(f"Error: Source directory '{src_dir}' not found.")
        sys.exit(1)
    
    # Process all sprite folders
    processed, skipped, errors = process_sprite_folder(src_dir, dest_dir)
    
    print("\nSummary:")
    print(f"  • Images trimmed: {processed}")
    print(f"  • Images unchanged: {skipped}")
    print(f"  • Errors: {errors}")
    print(f"\nTrimmed images saved to: {dest_dir}")

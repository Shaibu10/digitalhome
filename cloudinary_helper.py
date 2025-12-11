"""
Cloudinary Integration Module
Handles image uploads to Cloudinary cloud storage
"""

import os
import cloudinary
import cloudinary.uploader
from flask import current_app
from werkzeug.utils import secure_filename

# Configure Cloudinary
def init_cloudinary():
    """Initialize Cloudinary with environment variables"""
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
    api_key = os.environ.get('CLOUDINARY_API_KEY')
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')
    
    if cloud_name and api_key and api_secret:
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret
        )
        print(f"✅ Cloudinary initialized (cloud: {cloud_name})")
        return True
    else:
        print("⚠️  Cloudinary not configured - using local file storage (not persistent on Render)")
        return False

def upload_to_cloudinary(file, image_type='product', folder='digitalhome'):
    """
    Upload image to Cloudinary
    
    Args:
        file: FileStorage object from Flask
        image_type: Type of image (product, category, hero, etc)
        folder: Cloudinary folder path
        
    Returns:
        dict: Contains 'url' and 'public_id' or None if failed
    """
    try:
        if not file or file.filename == '':
            return None
            
        # Determine image dimensions based on type
        image_sizes = {
            'product': {'width': 600, 'height': 600, 'crop': 'fill'},
            'category': {'width': 400, 'height': 200, 'crop': 'fill'},
            'hero': {'width': 1200, 'height': 600, 'crop': 'fill'},
            'cart': {'width': 200, 'height': 200, 'crop': 'fill'},
            'recommended': {'width': 300, 'height': 300, 'crop': 'fill'},
        }
        
        dimensions = image_sizes.get(image_type, image_sizes['product'])
        
        # Upload to Cloudinary with automatic resizing
        response = cloudinary.uploader.upload(
            file,
            folder=f"{folder}/{image_type}",
            transformation=[
                {
                    'width': dimensions['width'],
                    'height': dimensions['height'],
                    'crop': dimensions['crop'],
                    'quality': 'auto'  # Automatic quality optimization
                }
            ],
            resource_type='auto'
        )
        
        return {
            'url': response['secure_url'],
            'public_id': response['public_id']
        }
        
    except Exception as e:
        print(f"❌ Cloudinary upload failed: {str(e)}")
        return None

def delete_from_cloudinary(public_id):
    """
    Delete image from Cloudinary
    
    Args:
        public_id: Cloudinary public ID of the image
        
    Returns:
        bool: True if deleted, False if failed
    """
    try:
        if not public_id:
            return False
            
        cloudinary.uploader.destroy(public_id)
        print(f"✅ Deleted from Cloudinary: {public_id}")
        return True
        
    except Exception as e:
        print(f"⚠️  Failed to delete from Cloudinary: {str(e)}")
        return False

def get_cloudinary_url(public_id, image_type='product', transformation=None):
    """
    Get optimized Cloudinary URL for image
    
    Args:
        public_id: Cloudinary public ID
        image_type: Type of image for default transformation
        transformation: Custom transformation dict
        
    Returns:
        str: Cloudinary secure URL
    """
    if not public_id:
        return None
        
    try:
        if transformation is None:
            # Default transformations for image types
            image_sizes = {
                'product': {'width': 600, 'height': 600, 'crop': 'fill'},
                'category': {'width': 400, 'height': 200, 'crop': 'fill'},
                'hero': {'width': 1200, 'height': 600, 'crop': 'fill'},
                'cart': {'width': 200, 'height': 200, 'crop': 'fill'},
                'thumbnail': {'width': 150, 'height': 150, 'crop': 'fill'},
            }
            transformation = image_sizes.get(image_type, image_sizes['product'])
        
        url = cloudinary.CloudinaryImage(public_id).build_url(
            transformation=transformation,
            secure=True
        )
        return url
        
    except Exception as e:
        print(f"❌ Failed to generate Cloudinary URL: {str(e)}")
        return None

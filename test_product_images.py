#!/usr/bin/env python
"""Verify product images are now showing correctly"""

import os
import requests
from app import app
from models import Product

def test_images():
    """Test that images are accessible and in the right location"""
    
    with app.app_context():
        products = Product.query.all()
        print("=" * 60)
        print("PRODUCT IMAGE VERIFICATION")
        print("=" * 60)
        print()
        
        for product in products:
            print(f"Product: {product.name}")
            print(f"  Database image name: {product.image}")
            
            # Check if file exists in static/uploads
            file_path = os.path.join('static/uploads', product.image)
            exists = os.path.exists(file_path)
            print(f"  File exists at {file_path}: {exists}")
            
            # Generate the URL that the template will use
            image_url = f"/static/uploads/{product.image}" if product.image else "/static/images/default-product.jpg"
            print(f"  Template image URL: {image_url}")
            print()
    
    # Now test HTTP requests
    print("=" * 60)
    print("HTTP REQUEST TESTS")
    print("=" * 60)
    print()
    
    # Test products page
    print("Testing /products page...")
    response = requests.get("http://localhost:5000/products")
    print(f"  Status: {response.status_code}")
    print(f"  Page contains product images: {'card-img-top' in response.text}")
    print()
    
    # Test product detail page
    print("Testing /product_detail page...")
    response = requests.get("http://localhost:5000/products/1")
    if response.status_code == 200:
        print(f"  Status: {response.status_code}")
        print(f"  Page contains image tag: {'img-fluid' in response.text}")
    else:
        print(f"  Status: {response.status_code}")
    print()
    
    # Test admin products page
    print("Testing /admin/products page...")
    session = requests.Session()
    
    # Login first
    login_response = session.post("http://localhost:5000/auth/login", data={
        'email': 'admin@example.com',
        'password': 'admin123'
    }, allow_redirects=True)
    
    if login_response.status_code == 200:
        admin_response = session.get("http://localhost:5000/admin/products")
        print(f"  Status: {admin_response.status_code}")
        print(f"  Page contains product images: {'object-fit: cover' in admin_response.text}")
    print()
    
    print("=" * 60)
    print("✅ IMAGE VERIFICATION COMPLETE!")
    print("=" * 60)

if __name__ == '__main__':
    test_images()

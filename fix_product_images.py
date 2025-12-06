#!/usr/bin/env python
"""Fix product image references"""

from app import app
from models import Product
from extensions import db

with app.app_context():
    products = Product.query.all()
    
    # List of available images
    available_images = [
        '20251105_031312_momo.PNG',
        '20251106_215155_IMG-20250709-WA0004_5.jpg',
        '20251106_215952_IMG-20250709-WA0004_6.jpg',
        '20251106_220818_IMG-20250709-WA0004_3.jpg',
        '20251107_010808_admin_dashboard.PNG',
        'IMG-20250709-WA0004_2.jpg',
        'IMG-20250709-WA0004_3.jpg'
    ]
    
    print(f"Found {len(products)} product(s)")
    print(f"Available images: {len(available_images)}")
    print()
    
    for i, product in enumerate(products):
        # Assign images to products
        if available_images:
            new_image = available_images[i % len(available_images)]
            print(f"Product: {product.name}")
            print(f"  Old image: {product.image}")
            print(f"  New image: {new_image}")
            product.image = new_image
            print()
    
    db.session.commit()
    print("✅ Product images updated successfully!")

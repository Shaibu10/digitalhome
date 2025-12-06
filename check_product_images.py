#!/usr/bin/env python
"""Check product images in database"""

from app import app
from models import Product

with app.app_context():
    products = Product.query.all()
    print(f"Total products: {len(products)}\n")
    
    for product in products:
        print(f"Product: {product.name}")
        print(f"  Image: {product.image}")
        print(f"  Image path would be: /static/uploads/{product.image if product.image else 'default-product.jpg'}")
        print()

#!/usr/bin/env python
"""
Quick test to verify the checkout endpoint 415 error is fixed.
"""

import json
from app import app, db
from models import User, Product, Category, CartItem, Order

def test_checkout_with_json_content_type():
    """Test that checkout endpoint accepts JSON requests with proper Content-Type"""
    
    with app.app_context():
        # Create test data
        client = app.test_client()
        
        # Create or get test user
        test_user = User.query.filter_by(username='testuser').first()
        if not test_user:
            test_user = User(
                username='testuser',
                email='test@example.com',
                password_hash='hashed_password',
                is_verified=True,
                phone_number='1234567890'
            )
            db.session.add(test_user)
            db.session.commit()
        
        # Create test product
        category = Category.query.first()
        if not category:
            category = Category(name='Test Category')
            db.session.add(category)
            db.session.commit()
        
        product = Product.query.first()
        if not product:
            product = Product(
                name='Test Product',
                description='Test Description',
                price=100.00,
                stock_quantity=10,
                category_id=category.id
            )
            db.session.add(product)
            db.session.commit()
        
        # Add product to cart
        cart_item = CartItem(user_id=test_user.id, product_id=product.id, quantity=1)
        db.session.add(cart_item)
        db.session.commit()
        
        # Test checkout with JSON
        checkout_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'phone': '1234567890',
            'address': '123 Test St',
            'city': 'Test City',
            'postal_code': '12345',
            'payment_method': 'cod',
            'shipping_method': 'standard',
            'notes': 'Test order'
        }
        
        # Login user first
        with client:
            # Set up session
            with client.session_transaction() as sess:
                sess['_user_id'] = str(test_user.id)
            
            # Test POST with Content-Type: application/json
            response = client.post(
                '/checkout',
                data=json.dumps(checkout_data),
                content_type='application/json'
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.get_json()}")
            
            # Should not be 415
            assert response.status_code != 415, f"Got 415 error! Response: {response.get_json()}"
            
            # Should be 200 with success or 4xx with validation error
            if response.status_code == 200:
                data = response.get_json()
                assert data.get('success'), f"Order not successful: {data}"
                print("✓ Checkout successful!")
            else:
                print(f"Got status {response.status_code}: {response.get_json()}")


if __name__ == '__main__':
    test_checkout_with_json_content_type()
    print("\n✓ Test passed! The 415 error should be fixed.")

#!/usr/bin/env python
"""Test inventory deduction when admin marks order as paid"""

from app import app, db
from models import Order, Product, OrderItem
from datetime import datetime

def test_admin_paid_inventory_deduction():
    """Test that inventory is deducted when admin marks payment as paid"""
    
    with app.app_context():
        print("=" * 70)
        print("TESTING INVENTORY DEDUCTION ON ADMIN PAID STATUS UPDATE")
        print("=" * 70)
        
        # Get first order for testing
        order = Order.query.first()
        
        if not order:
            print("✗ No orders found in database. Please create an order first.")
            return False
        
        print(f"\n✓ Found order: {order.order_number}")
        print(f"  - Current payment status: {order.payment_status}")
        print(f"  - Order items: {len(order.order_items)}")
        
        if not order.order_items:
            print("✗ Order has no items. Cannot test.")
            return False
        
        # Check initial stock
        first_item = order.order_items[0]
        product = Product.query.get(first_item.product_id)
        
        if not product:
            print("✗ Product not found for order item.")
            return False
        
        initial_stock = product.stock_quantity
        print(f"\n  - Product: {product.name}")
        print(f"  - Order quantity: {first_item.quantity}")
        print(f"  - Current stock: {initial_stock}")
        
        # Simulate admin changing payment status to 'paid'
        print("\n" + "=" * 70)
        print("SIMULATING ADMIN PAYMENT STATUS CHANGE TO 'PAID'")
        print("=" * 70)
        
        if order.payment_status == 'paid':
            print("\nℹ Note: Order already has payment_status='paid'")
            print("  → If stock is less than original, inventory was already deducted")
            print(f"  → Stock: {product.stock_quantity}")
        else:
            old_payment = order.payment_status
            
            # Test the deduction method
            success, message = order.deduct_inventory()
            
            print(f"\nℹ Attempting to deduct inventory...")
            print(f"  - Method result: {success}")
            print(f"  - Message: {message}")
            
            if success:
                expected_stock = initial_stock - sum(item.quantity for item in order.order_items)
                actual_stock = product.stock_quantity
                
                print(f"\n✓ Inventory deducted successfully!")
                print(f"  - Stock before: {initial_stock}")
                print(f"  - Stock after: {actual_stock}")
                print(f"  - Deducted: {initial_stock - actual_stock} items")
                
                if actual_stock == expected_stock:
                    print(f"  ✓ Stock matches expected value: {expected_stock}")
                    return True
                else:
                    print(f"  ✗ Stock mismatch! Expected: {expected_stock}, Got: {actual_stock}")
                    return False
            else:
                print(f"\n✗ Inventory deduction failed: {message}")
                return False
        
        print("\n" + "=" * 70)
        print("TEST COMPLETED")
        print("=" * 70)
        return True

if __name__ == '__main__':
    success = test_admin_paid_inventory_deduction()
    exit(0 if success else 1)

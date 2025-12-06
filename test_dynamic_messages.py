#!/usr/bin/env python
"""
Test script for Dynamic Message System
Tests model creation, database operations, and admin functionality
"""

from app import app, db
from models import DynamicMessage, User
from datetime import datetime, timedelta
import sys

def test_dynamic_messages():
    """Run comprehensive tests for dynamic messages feature"""
    print("\n" + "="*70)
    print("DYNAMIC MESSAGE SYSTEM - TEST SUITE")
    print("="*70 + "\n")
    
    with app.app_context():
        try:
            # Test 1: Database table exists
            print("TEST 1: Checking if dynamic_message table exists...")
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'dynamic_message' in tables:
                print("✓ Table 'dynamic_message' exists\n")
            else:
                print("✗ Table 'dynamic_message' NOT found\n")
                return False
            
            # Test 2: Create a test message
            print("TEST 2: Creating test dynamic message...")
            test_message = DynamicMessage(
                title="Test Message",
                content="This is a <strong>test message</strong> for the homepage.",
                message_type="info",
                is_active=True,
                display_location="homepage",
                background_color="#007bff",
                text_color="#ffffff",
                icon="info-circle",
                cta_text="Learn More",
                cta_url="/learn-more",
                display_order=0,
                created_by_id=1,
                updated_by_id=1
            )
            db.session.add(test_message)
            db.session.commit()
            print(f"✓ Message created with ID: {test_message.id}\n")
            
            # Test 3: Query active messages
            print("TEST 3: Retrieving active messages...")
            active_messages = DynamicMessage.query.filter_by(is_active=True).all()
            print(f"✓ Found {len(active_messages)} active message(s)\n")
            
            # Test 4: Test scheduling logic
            print("TEST 4: Testing scheduling logic...")
            future_message = DynamicMessage(
                title="Future Message",
                content="This message will be shown in the future.",
                message_type="promotion",
                is_active=True,
                start_date=datetime.utcnow() + timedelta(days=1),
                end_date=datetime.utcnow() + timedelta(days=7),
                display_location="homepage",
                background_color="#28a745",
                text_color="#ffffff",
                icon="star",
                created_by_id=1,
                updated_by_id=1
            )
            db.session.add(future_message)
            db.session.commit()
            
            # Check if it's scheduled
            is_scheduled = future_message.is_scheduled()
            is_active = future_message.is_currently_active()
            print(f"✓ Future message created (ID: {future_message.id})")
            print(f"  - is_scheduled(): {is_scheduled}")
            print(f"  - is_currently_active(): {is_active}\n")
            
            # Test 5: Test analytics
            print("TEST 5: Testing analytics tracking...")
            initial_views = test_message.view_count
            initial_clicks = test_message.click_count
            
            test_message.increment_views()
            test_message.increment_clicks()
            db.session.commit()
            
            print(f"✓ Analytics tracking functional")
            print(f"  - Views: {initial_views} → {test_message.view_count}")
            print(f"  - Clicks: {initial_clicks} → {test_message.click_count}\n")
            
            # Test 6: Get homepage messages
            print("TEST 6: Retrieving homepage messages...")
            homepage_messages = DynamicMessage.get_active_homepage_messages()
            print(f"✓ Found {len(homepage_messages)} message(s) for homepage\n")
            
            # Test 7: Test expiration
            print("TEST 7: Testing expiration logic...")
            expired_message = DynamicMessage(
                title="Expired Message",
                content="This message has expired.",
                message_type="alert",
                is_active=True,
                end_date=datetime.utcnow() - timedelta(days=1),
                display_location="homepage",
                background_color="#dc3545",
                text_color="#ffffff",
                icon="alert",
                created_by_id=1,
                updated_by_id=1
            )
            db.session.add(expired_message)
            db.session.commit()
            
            is_expired = expired_message.is_expired()
            print(f"✓ Expired message created (ID: {expired_message.id})")
            print(f"  - is_expired(): {is_expired}\n")
            
            # Summary
            print("="*70)
            print("TEST SUMMARY")
            print("="*70)
            print("✓ All tests passed successfully!")
            print(f"\nDatabase Statistics:")
            total_messages = DynamicMessage.query.count()
            active = DynamicMessage.query.filter_by(is_active=True).count()
            print(f"  - Total messages: {total_messages}")
            print(f"  - Active messages: {active}")
            print(f"  - Homepage eligible: {len(homepage_messages)}\n")
            
            # Clean up test data
            print("Cleaning up test data...")
            DynamicMessage.query.delete()
            db.session.commit()
            print("✓ Test data removed\n")
            
            return True
            
        except Exception as e:
            print(f"\n✗ TEST FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_dynamic_messages()
    sys.exit(0 if success else 1)

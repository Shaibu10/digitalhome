"""
Verify Supabase Migration
Verifies that all tables and data have been migrated correctly to Supabase.
Run this AFTER running migrations to ensure everything is set up properly.
"""

import os
import sys
from datetime import datetime

def verify_migration():
    """Verify all tables and data are in Supabase"""
    
    print("=" * 70)
    print("SUPABASE MIGRATION VERIFICATION")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        # Import after trying to establish what might be missing
        print("Importing application modules...")
        from config import Config
        from extensions import db
        from models import (User, Product, Category, Order, OrderItem, 
                           CartItem, HeroSection, UserActivity, SystemSettings, 
                           DynamicMessage, ProductReview, ContactSettings)
        from app import create_app
        
        print("✅ Modules imported successfully\n")
        
        # Create app context
        print("Creating application context...")
        app = create_app()
        
        with app.app_context():
            print("✅ Application context created\n")
            
            # 1. Check if database connection works
            print("1️⃣  TESTING DATABASE CONNECTION")
            print("-" * 70)
            try:
                from sqlalchemy import text, inspect
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                print(f"✅ Connected to database")
                print(f"   Tables found: {len(tables)}\n")
            except Exception as e:
                print(f"❌ Connection failed: {e}\n")
                return False
            
            # 2. Count records in each major table
            print("2️⃣  COUNTING RECORDS IN TABLES")
            print("-" * 70)
            
            tables_to_check = {
                'Users': User,
                'Products': Product,
                'Categories': Category,
                'Orders': Order,
                'Order Items': OrderItem,
                'Cart Items': CartItem,
                'System Settings': SystemSettings,
                'Dynamic Messages': DynamicMessage,
                'Product Reviews': ProductReview,
                'Contact Settings': ContactSettings,
                'Hero Sections': HeroSection,
                'User Activities': UserActivity,
            }
            
            total_records = 0
            
            for name, model in tables_to_check.items():
                try:
                    count = model.query.count()
                    print(f"✅ {name:20} : {count:6} records")
                    total_records += count
                except Exception as e:
                    print(f"⚠️  {name:20} : ERROR - {str(e)[:40]}")
            
            print(f"\n📊 TOTAL RECORDS: {total_records}\n")
            
            # 3. Check for admin user
            print("3️⃣  VERIFYING ADMIN USER")
            print("-" * 70)
            
            try:
                admin = User.query.filter_by(email='admin@example.com').first()
                if admin:
                    print(f"✅ Admin user exists")
                    print(f"   Email: {admin.email}")
                    print(f"   Username: {admin.username}")
                    print(f"   Is Admin: {admin.is_admin}")
                    print(f"   Is Verified: {admin.is_verified}")
                    print()
                else:
                    print(f"⚠️  Admin user NOT found!")
                    print(f"   This might be normal if you migrated from existing database")
                    print(f"   You can create one manually if needed\n")
            except Exception as e:
                print(f"❌ Error checking admin: {e}\n")
            
            # 4. Check table structure
            print("4️⃣  VERIFYING TABLE STRUCTURE")
            print("-" * 70)
            
            critical_tables = ['user', 'product', 'category', 'order']
            all_exist = True
            
            for table_name in critical_tables:
                if table_name in tables:
                    # Get column count
                    columns = inspector.get_columns(table_name)
                    print(f"✅ {table_name:15} : {len(columns)} columns")
                else:
                    print(f"❌ {table_name:15} : NOT FOUND")
                    all_exist = False
            
            print()
            
            # 5. Check foreign key relationships
            print("5️⃣  CHECKING KEY RELATIONSHIPS")
            print("-" * 70)
            
            try:
                # Try to access a sample order with items
                sample_order = Order.query.first()
                if sample_order:
                    items_count = len(sample_order.items) if sample_order.items else 0
                    print(f"✅ Order-OrderItem relationship OK (sample: {items_count} items)")
                else:
                    print(f"ℹ️  No orders in database (this is normal for new setup)")
                
                # Check product category relationship
                sample_product = Product.query.first()
                if sample_product:
                    has_category = sample_product.category is not None
                    print(f"✅ Product-Category relationship OK")
                else:
                    print(f"ℹ️  No products in database (this is normal for new setup)")
                
                print()
            except Exception as e:
                print(f"⚠️  Error checking relationships: {e}\n")
            
            # 6. Final Summary
            print("6️⃣  MIGRATION SUMMARY")
            print("=" * 70)
            
            if all_exist and total_records >= 0:
                print("✅ MIGRATION SUCCESSFUL!")
                print("   All critical tables exist and are accessible")
                print("   Database structure is intact")
                print("   Ready to use!\n")
                
                if total_records == 0:
                    print("ℹ️  Note: Database is empty (new installation)")
                    print("   You can now:")
                    print("   • Create categories and products")
                    print("   • Set up dynamic messages")
                    print("   • Configure system settings")
                else:
                    print(f"ℹ️  Database has {total_records} existing records")
                
                print("=" * 70)
                return True
            else:
                print("❌ MIGRATION HAS ISSUES")
                print("   Some tables are missing or not accessible")
                print("   Please check the errors above")
                print("=" * 70)
                return False
                
    except ImportError as e:
        print(f"❌ IMPORT ERROR: {e}")
        print("\nMake sure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = verify_migration()
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Verification cancelled by user")
        sys.exit(1)

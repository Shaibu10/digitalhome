"""
Test Supabase Connection
Tests if the database connection to Supabase is working correctly.
Run this BEFORE running migrations to verify connectivity.
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect

def test_connection():
    """Test basic database connection"""
    
    # Get database URL from environment or use placeholder
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if not DATABASE_URL:
        print("❌ ERROR: DATABASE_URL environment variable not set!")
        print("\nSet it with:")
        print("  PowerShell: $env:DATABASE_URL=\"your-connection-string\"")
        print("  Bash: export DATABASE_URL=\"your-connection-string\"")
        print("\nOr update your .env file with:")
        print("  DATABASE_URL=postgresql://postgres:password@db.region.supabase.co:5432/postgres")
        return False
    
    # Mask password in display
    display_url = DATABASE_URL.replace('postgres:', 'postgres:***')
    display_url = display_url[:display_url.rfind('@') + 1] if '@' in display_url else display_url
    
    print("=" * 70)
    print("SUPABASE CONNECTION TEST")
    print("=" * 70)
    print(f"Testing connection to: {display_url}...")
    
    try:
        # Try to create connection
        engine = create_engine(DATABASE_URL)
        
        # Test the connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            value = result.fetchone()[0]
            
            if value == 1:
                print("\n✅ CONNECTION SUCCESSFUL!")
                print(f"   Database is responding correctly")
                
                # Get database info
                inspector = inspect(engine)
                tables = inspector.get_table_names()
                
                print(f"\n📊 DATABASE INFORMATION:")
                print(f"   Total tables: {len(tables)}")
                if tables:
                    print(f"   Tables found:")
                    for table in sorted(tables):
                        print(f"     - {table}")
                else:
                    print(f"   ℹ️  No tables yet (this is normal before migration)")
                
                print("\n" + "=" * 70)
                print("✅ Ready to run migrations!")
                print("=" * 70)
                return True
            else:
                print(f"❌ Unexpected response: {value}")
                return False
                
    except ImportError as e:
        print(f"\n❌ IMPORT ERROR: {e}")
        print("\nMissing required package. Install it with:")
        print("  pip install psycopg[binary]")
        return False
        
    except Exception as e:
        print(f"\n❌ CONNECTION FAILED!")
        print(f"   Error: {str(e)}")
        
        # Provide specific troubleshooting
        error_msg = str(e).lower()
        
        if "could not resolve" in error_msg or "name or service not known" in error_msg:
            print("\n🔍 Troubleshooting:")
            print("   • Check database URL host is correct")
            print("   • Verify Supabase project is running")
            print("   • Check internet connection")
            
        elif "password authentication failed" in error_msg:
            print("\n🔍 Troubleshooting:")
            print("   • Check password is correct")
            print("   • Ensure no special characters in password")
            print("   • Verify you copied the full connection string")
            
        elif "timeout" in error_msg or "timed out" in error_msg:
            print("\n🔍 Troubleshooting:")
            print("   • Check firewall settings")
            print("   • Verify network connectivity")
            print("   • Try again in a few moments")
            
        elif "psycopg" in error_msg or "psycopg2" in error_msg:
            print("\n🔍 Troubleshooting:")
            print("   • Install psycopg: pip install psycopg[binary]")
            
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

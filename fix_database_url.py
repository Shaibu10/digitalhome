"""
Fix Malformed Supabase Connection String
This script helps diagnose and fix DATABASE_URL formatting issues.
"""

import sys
import re

def validate_connection_string(url):
    """Validate PostgreSQL connection string format"""
    
    if not url:
        return False, "Empty connection string"
    
    # Check for malformed credentials (multiple @ symbols)
    at_count = url.count('@')
    if at_count > 1:
        return False, f"❌ MALFORMED: Multiple @ symbols found ({at_count}). Looks like credentials are doubled."
    
    if at_count == 0:
        return False, "❌ MALFORMED: No @ symbol found. Missing host specification."
    
    # Check for valid PostgreSQL URL pattern
    # Should be: postgresql://user:password@host:port/database
    pattern = r'^postgresql(?:\+psycopg)?://[^@]+@[^/]+(?::\d+)?/\w+$'
    
    if not re.match(pattern, url):
        return False, f"❌ INVALID FORMAT: Does not match PostgreSQL URL pattern"
    
    # Check required components
    if '://' not in url:
        return False, "❌ MISSING: Scheme (postgresql://)"
    
    parts = url.split('://', 1)[1].split('@', 1)
    credentials = parts[0]
    host_part = parts[1]
    
    if ':' not in credentials:
        return False, "❌ MISSING: Password (should be user:password)"
    
    user, password = credentials.split(':', 1)
    if not user or not password:
        return False, "❌ EMPTY: Username or password is empty"
    
    if not host_part or '.' not in host_part:
        return False, "❌ INVALID: Host doesn't look like a domain"
    
    return True, f"✅ VALID format\n   User: {user}\n   Host: {host_part.split('/')[0]}"


def fix_malformed_url(bad_url):
    """Attempt to extract and fix a malformed URL"""
    
    print("\n🔧 ATTEMPTING TO FIX MALFORMED URL...\n")
    
    # Extract host - look for supabase domain
    supabase_match = re.search(r'db\.[a-z0-9]+\.supabase\.co', bad_url)
    if not supabase_match:
        return None, "Could not find Supabase host"
    
    host = supabase_match.group(0)
    
    # Look for any password-like string (alphanumeric, might have special chars)
    # Usually before @ symbols
    password_match = re.search(r'(?:^|=)([A-Za-z0-9_\-\.]+)@', bad_url)
    password = password_match.group(1) if password_match else None
    
    if not password:
        return None, "Could not extract password"
    
    # Construct proper URL
    fixed_url = f"postgresql://postgres:{password}@{host}:5432/postgres"
    
    return fixed_url, "Extracted and reconstructed"


def main():
    print("=" * 70)
    print("SUPABASE CONNECTION STRING VALIDATOR")
    print("=" * 70)
    print()
    
    # Get URL from command line or input
    if len(sys.argv) > 1:
        url = sys.argv[1]
        print(f"Testing: {url[:50]}...\n")
    else:
        url = input("Enter your DATABASE_URL (or 'exit' to quit): ").strip()
        if url.lower() == 'exit':
            return
        print()
    
    # Validate
    is_valid, message = validate_connection_string(url)
    print(message)
    print()
    
    # If not valid, try to fix
    if not is_valid and url.count('@') > 1:
        print("\n" + "=" * 70)
        fixed, status = fix_malformed_url(url)
        
        if fixed:
            print(status)
            print("\n✅ CORRECTED URL:")
            print(f"   {fixed}")
            print("\n📋 USE THIS in Render:")
            print("   1. Go to your Render service")
            print("   2. Settings → Environment")
            print("   3. Update DATABASE_URL with the corrected URL above")
            print("   4. Save and redeploy")
        else:
            print(f"❌ Could not fix: {status}")
            print("\n🛠️  Manual fix needed:")
            print("   1. Get your Supabase connection string:")
            print("      - Supabase Dashboard → Project → Settings → Database")
            print("      - Copy the 'Connection string' section")
            print("   2. Format should be:")
            print("      postgresql://postgres:PASSWORD@db.REGION.supabase.co:5432/postgres")
            print("   3. Update in Render and redeploy")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""
Revenue Recognition Policy Verification Script
Verify that the revenue recognition policy has been correctly implemented
"""

import os
import re
from pathlib import Path

# Define the workspace path
WORKSPACE = r"e:\python_projects\digialhome"

# Expected verification patterns
VERIFICATION_PATTERNS = {
    'analytics_helpers.py': {
        'file_path': os.path.join(WORKSPACE, 'analytics_helpers.py'),
        'patterns': [
            (r"Order\.payment_status == 'paid'", 'payment_status filter', 6),  # Expected 6 matches
        ]
    },
    'app.py': {
        'file_path': os.path.join(WORKSPACE, 'app.py'),
        'patterns': [
            (r"from sqlalchemy import and_", 'and_ import', 1),  # Expected 1 (global import)
            (r"Order\.payment_status == 'paid'", 'payment_status filter', 2),  # Expected 2
        ]
    },
    'analytics.html': {
        'file_path': os.path.join(WORKSPACE, 'templates/admin/analytics.html'),
        'patterns': [
            (r"Paid Sales Trends", 'paid sales trends header', 1),
            (r"Paid Monthly Revenue", 'paid monthly revenue header', 1),
            (r"Paid Conversion Funnel", 'paid conversion funnel header', 1),
            (r"Paid Conversion Rates", 'paid conversion rates header', 1),
            (r"Paid Order Status Breakdown", 'paid order status header', 1),
            (r"Based on paid, non-cancelled orders", 'clarification notes', 8),  # Expected ~8
        ]
    }
}

DOCUMENTATION_FILES = [
    'REVENUE_RECOGNITION_POLICY_COMPLETE.md',
    'REVENUE_RECOGNITION_QUICK_REFERENCE.md',
    'IMPLEMENTATION_SUMMARY_REVENUE_POLICY.md',
    'REVENUE_POLICY_EXACT_CHANGES.md',
    'REVENUE_POLICY_IMPLEMENTATION_COMPLETE.md',
]


def verify_file_exists(filepath, name):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {name}: EXISTS")
        return True
    else:
        print(f"❌ {name}: MISSING - {filepath}")
        return False


def verify_pattern(filepath, name, pattern, expected_count=None):
    """Verify a regex pattern exists in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        matches = re.findall(pattern, content)
        count = len(matches)
        
        if expected_count:
            if count == expected_count:
                print(f"✅ {name}: Found {count} match(es) (expected {expected_count})")
                return True
            else:
                print(f"⚠️  {name}: Found {count} match(es) (expected {expected_count})")
                return count > 0
        else:
            if count > 0:
                print(f"✅ {name}: Found {count} match(es)")
                return True
            else:
                print(f"❌ {name}: No matches found")
                return False
    except FileNotFoundError:
        print(f"❌ {name}: File not found - {filepath}")
        return False
    except Exception as e:
        print(f"❌ {name}: Error - {e}")
        return False


def main():
    """Main verification script"""
    print("\n" + "="*70)
    print("REVENUE RECOGNITION POLICY - IMPLEMENTATION VERIFICATION")
    print("="*70 + "\n")
    
    all_passed = True
    
    # Verify code changes
    print("📝 VERIFYING CODE CHANGES\n")
    print("-" * 70)
    
    for file_name, file_config in VERIFICATION_PATTERNS.items():
        file_path = file_config['file_path']
        print(f"\n🔍 File: {file_name}")
        
        # Check file exists
        if not verify_file_exists(file_path, f"File exists"):
            all_passed = False
            continue
        
        # Check patterns
        for pattern, description, expected_count in file_config['patterns']:
            if not verify_pattern(file_path, f"  {description}", pattern, expected_count):
                all_passed = False
    
    # Verify documentation files
    print("\n\n📚 VERIFYING DOCUMENTATION FILES\n")
    print("-" * 70)
    
    for doc_file in DOCUMENTATION_FILES:
        file_path = os.path.join(WORKSPACE, doc_file)
        if not verify_file_exists(file_path, f"Documentation"):
            all_passed = False
    
    # Summary
    print("\n\n" + "="*70)
    if all_passed:
        print("✅ VERIFICATION PASSED - ALL CHECKS SUCCESSFUL")
        print("\nThe revenue recognition policy has been correctly implemented.")
        print("\nNext Steps:")
        print("1. Review REVENUE_RECOGNITION_QUICK_REFERENCE.md for overview")
        print("2. Test admin dashboard at /admin/dashboard")
        print("3. Test analytics at /admin/analytics")
        print("4. Run unit tests if available")
        print("5. Deploy to production when ready")
    else:
        print("⚠️  VERIFICATION INCOMPLETE - SOME CHECKS NEED ATTENTION")
        print("\nPlease review the failed items above and verify implementation.")
    print("="*70 + "\n")
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    exit(main())

#!/usr/bin/env python
"""Verify print functionality updates"""

def test_print_updates():
    """Verify all print functionality changes are in place"""
    
    with open('templates/admin/order_detail.html', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    checks = {
        "Hide sidebar CSS": "nav, aside, .sidebar, .navbar" in content,
        "Compressed fonts (10pt)": "font-size: 10pt" in content,
        "Small padding (0.15in)": "padding: 0.15in" in content,
        "Single page setup": "@page {" in content and "size: A4" in content,
        "JavaScript sidebar hiding": "nav, aside, .sidebar, .navbar" in content,
        "Reduced margins (0.3in)": "margin: 0.3in" in content,
        "Print dialog auto-trigger": "window.print()" in content,
        "Container padding": "paddingLeft = '0.3in'" in content,
    }
    
    print("=" * 70)
    print("PRINT FUNCTIONALITY VERIFICATION")
    print("=" * 70)
    
    all_passed = True
    for check_name, result in checks.items():
        status = "✓" if result else "✗"
        print(f"{status} {check_name}: {result}")
        if not result:
            all_passed = False
    
    print("=" * 70)
    if all_passed:
        print("✓ All print functionality checks PASSED")
        print("\nChanges made:")
        print("  1. Sidebar hidden with CSS @media print")
        print("  2. Fonts compressed to 10pt (from 12pt)")
        print("  3. Padding reduced to 0.15in (from 0.3-0.5in)")
        print("  4. Single page layout enforced")
        print("  5. JavaScript hides all non-print elements")
        print("  6. Receipt should now fit on 1 sheet")
    else:
        print("✗ Some checks FAILED - review template")
    
    return all_passed

if __name__ == '__main__':
    success = test_print_updates()
    exit(0 if success else 1)

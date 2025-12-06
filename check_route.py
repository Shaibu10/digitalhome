"""
Check if calculate-checkout route is registered
"""
import sys
sys.path.insert(0, 'e:\\python_projects\\digialhome')

from app import app

api_routes = [r for r in app.url_map.iter_rules() if '/api/' in str(r) and 'sms' not in str(r)]
print(f"\n[FOUND {len(api_routes)} API routes]")

for r in api_routes:
    print(f"  {r}")

print("\n[CHECKING for calculate route...]")
calculate_routes = [r for r in app.url_map.iter_rules() if 'calculate' in str(r)]
print(f"[CALCULATE routes: {len(calculate_routes)}]")

if calculate_routes:
    for r in calculate_routes:
        print(f"  {r}")
else:
    print("  NO CALCULATE ROUTES FOUND")
    print("\n[Looking for all checkout-related routes...]")
    checkout_routes = [r for r in app.url_map.iter_rules() if 'checkout' in str(r)]
    for r in checkout_routes:
        print(f"  {r}")

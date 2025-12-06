"""
List all registered routes in the Flask app
"""
import sys
sys.path.insert(0, 'e:\\python_projects\\digialhome')

from app import app

with app.app_context():
    print("\n[ROUTES] All registered Flask routes:")
    print("=" * 80)
    
    routes = []
    for rule in app.url_map.iter_rules():
        if 'calculate' in rule.rule or 'api' in rule.rule:
            methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
            routes.append((rule.rule, methods))
    
    for route, methods in sorted(routes):
        print(f"{route:50} [{methods}]")
    
    print("\n[CHECK] Looking for calculate-checkout route...")
    found = False
    for rule in app.url_map.iter_rules():
        if 'calculate' in rule.rule:
            print(f"  FOUND: {rule.rule} [{','.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
            found = True
    
    if not found:
        print("  NOT FOUND - Need to check if endpoint was added correctly")

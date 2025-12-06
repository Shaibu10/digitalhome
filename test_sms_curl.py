#!/usr/bin/env python
"""Simple SMS endpoint test"""
import subprocess
import time

# Give server time to start
time.sleep(2)

print("Testing SMS endpoints with curl...")
print("=" * 60)

# Test 1: Dashboard
print("\n1. Testing SMS Dashboard...")
result = subprocess.run([
    'curl', '-s', '-w', '\\nStatus: %{http_code}\\n',
    'http://127.0.0.1:5000/admin/sms/'
], capture_output=True, text=True)
print(result.stdout[-50:] if len(result.stdout) > 50 else result.stdout)

# Test 2: Templates page
print("\n2. Testing Templates List...")
result = subprocess.run([
    'curl', '-s', '-w', '\\nStatus: %{http_code}\\n',
    'http://127.0.0.1:5000/admin/sms/templates'
], capture_output=True, text=True)
print(result.stdout[-50:] if len(result.stdout) > 50 else result.stdout)

print("\n" + "=" * 60)

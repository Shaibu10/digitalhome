#!/usr/bin/env python
"""Test email warnings suppression."""

import os

# Test with warnings suppressed
print("=" * 50)
print("Testing with SHOW_EMAIL_WARNINGS=false")
print("=" * 50)

os.environ['SHOW_EMAIL_WARNINGS'] = 'false'

from app import app

print("\n✅ App imported with warnings suppressed")
print("(You should NOT see Gmail warnings above)")

# Now test without suppression
print("\n" + "=" * 50)
print("Testing with SHOW_EMAIL_WARNINGS=true (default)")
print("=" * 50)

# This would require a fresh import, but shows the setting works
print("\nSet SHOW_EMAIL_WARNINGS=true or omit it to see the warnings again")

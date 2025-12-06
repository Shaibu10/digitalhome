#!/usr/bin/env python
"""Initialize database directly"""

import os
import sys

# Change to script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Import app and init function
from app import app, init_db

# Initialize the database
print("Initializing database...")
try:
    init_db()
    print("✓ Database initialized successfully!")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

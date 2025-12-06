#!/usr/bin/env python
"""
DigitalHome - Development Server Launcher

Starts the Flask development server with appropriate settings.
Email warnings are suppressed by default for clean console output.
Set SHOW_EMAIL_WARNINGS=true to see Gmail API initialization details.
"""

import os

# Suppress Gmail warnings by default in development for clean output
if 'SHOW_EMAIL_WARNINGS' not in os.environ:
    os.environ['SHOW_EMAIL_WARNINGS'] = 'false'

from app import app

if __name__ == '__main__':   
    print("=" * 70)
    print(" 🚀 DigitalHome E-Commerce Platform - Development Server")
    print("=" * 70)
    print(f" 📍 Server running at: http://localhost:5000")
    print(f" 🔑 Admin login: admin@example.com / admin123")
    print(f" 📧 Email system: Console logging (development mode)")
    print("=" * 70)
    print("")
    
    app.run(debug=True)
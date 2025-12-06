#!/usr/bin/env python
"""Run Flask app without auto-reload"""
import os
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '0'

from app import create_app

app = create_app()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 DigitalHome E-Commerce Platform")
    print("="*60)
    print("📍 Server: http://localhost:5000")
    print("🔑 Admin: admin@example.com / admin123")
    print("📧 Email: Console logging (development)")
    print("="*60 + "\n")
    
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

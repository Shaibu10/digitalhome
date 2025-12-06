#!/usr/bin/env python
from app import app, db
from models import User
import sqlite3

with app.app_context():
    # Check SMS tables exist
    conn = sqlite3.connect('instance/app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    print('Database tables:')
    for table in sorted(tables):
        print(f'  - {table}')
    conn.close()
    
    # Create admin user
    if not User.query.filter_by(email='admin@example.com').first():
        admin = User(
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('\n✅ Admin user created: admin@example.com / admin123')
    else:
        print('\nℹ️ Admin user already exists')

from app import app
from models import ContactSettings

with app.app_context():
    settings = ContactSettings.get_settings()
    print('✓ ContactSettings table created and working')
    print(f'Business Name: {settings.business_name}')
    print(f'Email: {settings.email}')
    print(f'Phone: {settings.phone}')
    print(f'ID: {settings.id}')
    print('✓ Default contact settings initialized successfully')

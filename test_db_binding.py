from app import create_app
from extensions import db
from models import Payment, PaymentLog

app = create_app()

print(f"App config DATABASE_URL: {app.config.get('SQLALCHEMY_DATABASE_URI')}")

with app.app_context():
    print(f"DB engine in context: {db.engine}")
    print(f"DB metadata tables BEFORE create_all: {list(db.metadata.tables.keys())}")
    
    # Try creating tables
    db.create_all()
    
    print(f"DB metadata tables AFTER create_all: {list(db.metadata.tables.keys())}")
    
    # Check what Payment model knows
    print(f"\nPayment model: {Payment}")
    print(f"Payment tablename: {Payment.__tablename__}")
    print(f"Payment table: {Payment.__table__}")


#!/usr/bin/env python
"""Debug model registration."""

import os

print("Before imports...")

from extensions import db

print(f"After importing db: tables in metadata: {list(db.metadata.tables.keys())}")

from models import User, Category, Product, Order, OrderItem, CartItem, HeroSection, UserActivity, EmailToken, TokenRateLimit

print(f"After importing models: tables in metadata: {list(db.metadata.tables.keys())}")

# Check User model directly
print(f"\nUser model columns:")
for col in User.__table__.columns:
    print(f"  - {col.name}")

print("\n✓ Done")

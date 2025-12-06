from app import app, db
from models import ProductReview

with app.app_context():
    # Check all reviews
    all_reviews = ProductReview.query.all()
    print(f'Total reviews in database: {len(all_reviews)}')
    
    # Check pending reviews
    pending = ProductReview.query.filter_by(is_approved=False).all()
    print(f'Pending reviews (not approved): {len(pending)}')
    
    # Check approved reviews
    approved = ProductReview.query.filter_by(is_approved=True).all()
    print(f'Approved reviews: {len(approved)}')
    
    if pending:
        print('\nPending reviews:')
        for rev in pending[:5]:
            print(f'  ID {rev.id}: "{rev.title}" (Product {rev.product_id}, User {rev.user_id})')
    
    if approved:
        print('\nApproved reviews:')
        for rev in approved[:5]:
            print(f'  ID {rev.id}: "{rev.title}" (Product {rev.product_id}, User {rev.user_id})')

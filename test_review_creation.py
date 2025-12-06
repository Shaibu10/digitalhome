from app import app, db
from models import ProductReview, User

with app.app_context():
    # Get user 1 (has purchased product 5)
    user = User.query.get(1)
    
    if user:
        print(f'Creating test review for user: {user.username}')
        
        review = ProductReview(
            product_id=5,
            user_id=user.id,
            rating=5,
            title='Excellent product!',
            content='This product is absolutely fantastic! I really love it and would recommend it to anyone. Great quality and value for money. Very satisfied with my purchase.',
            is_approved=False
        )
        
        db.session.add(review)
        db.session.commit()
        
        print(f'✓ Review created with ID: {review.id}')
        
        # Verify it's in the database
        pending = ProductReview.query.filter_by(is_approved=False).all()
        print(f'Pending reviews in database: {len(pending)}')
        
        if pending:
            print('\nPending reviews:')
            for r in pending:
                print(f'  - ID {r.id}: {r.title} (Product {r.product_id})')

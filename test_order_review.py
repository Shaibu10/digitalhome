from app import app, db
from models import Order, ProductReview

with app.app_context():
    # Find a delivered order
    order = Order.query.filter_by(status='delivered').first()
    
    if order:
        print(f'Found delivered order: {order.order_number}')
        print(f'Items in order: {len(order.order_items)}')
        
        # Clear any existing reviews from this test
        for item in order.order_items:
            existing = ProductReview.query.filter_by(
                product_id=item.product_id,
                user_id=order.user_id
            ).all()
            for rev in existing:
                db.session.delete(rev)
        db.session.commit()
        
        # Simulate the review submission
        rating = 5
        comment = 'This is an excellent product! Very satisfied with my purchase.'
        
        reviews_created = 0
        for item in order.order_items:
            review = ProductReview(
                product_id=item.product_id,
                user_id=order.user_id,
                rating=rating,
                title=f'Review from Order {order.order_number}',
                content=comment,
                is_approved=False
            )
            db.session.add(review)
            reviews_created += 1
        
        db.session.commit()
        
        print(f'✓ Created {reviews_created} reviews')
        
        # Verify they're in the database
        pending = ProductReview.query.filter_by(is_approved=False).all()
        print(f'Total pending reviews in database: {len(pending)}')
        
        if pending:
            print('\nPending reviews:')
            for r in pending[:5]:
                print(f'  - ID {r.id}: "{r.title}" (Product {r.product_id}, User {r.user_id})')
    else:
        print('No delivered orders found')

from app import app, db
from models import Order, OrderItem, User, Product

with app.app_context():
    # Check users
    users = User.query.all()
    print(f'Total users: {len(users)}')
    
    # Check products
    products = Product.query.all()
    print(f'Total products: {len(products)}')
    
    # Check orders
    orders = Order.query.all()
    print(f'Total orders: {len(orders)}')
    
    if orders:
        print('\nOrders:')
        for order in orders[:5]:
            print(f'  Order #{order.id}: User {order.user_id}, Status: {order.status}')
            items = OrderItem.query.filter_by(order_id=order.id).all()
            for item in items:
                print(f'    - Product {item.product_id} x{item.quantity}')
    else:
        print('\n⚠️ No orders in database - users cannot submit reviews without orders!')

# Professional Order & Cart System - Quick Reference

**Last Updated:** November 28, 2025

---

## Quick Links

| Feature | File | Location |
|---------|------|----------|
| Order Model | `models.py` | Lines 126-176 |
| OrderItem Model | `models.py` | Lines 178-189 |
| CartItem Model | `models.py` | Lines 191-211 |
| Backend Routes | `app.py` | Lines 557-839 |
| Cart Template | `templates/cart.html` | Entire file |
| Checkout Template | `templates/checkout.html` | Entire file |
| Confirmation Template | `templates/order_confirmation.html` | Entire file |
| History Template | `templates/order_history.html` | Entire file |
| Detail Template | `templates/order_detail.html` | Entire file |

---

## Common Tasks

### Create an Order Programmatically

```python
from models import Order, OrderItem, CartItem
from datetime import datetime

# Get cart items
cart_items = CartItem.query.filter_by(user_id=user_id).all()

# Calculate totals
subtotal = sum(item.product.final_price() * item.quantity for item in cart_items)
shipping = 10.00
tax = subtotal * 0.05
total = subtotal + shipping + tax

# Create order
order = Order(
    user_id=user_id,
    order_number=f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
    subtotal=subtotal,
    shipping_cost=shipping,
    discount_amount=0,
    discount_percentage=0,
    total_amount=total,
    status='pending',
    payment_method='cod',
    payment_status='unpaid',
    shipping_address='123 Main St',
    shipping_city='Accra',
    shipping_postal_code='00233',
    shipping_phone='0241234567'
)

# Add items
for cart_item in cart_items:
    order.order_items.append(OrderItem(
        product_id=cart_item.product_id,
        product_name=cart_item.product.name,
        quantity=cart_item.quantity,
        unit_price=cart_item.product.final_price(),
        total_price=cart_item.product.final_price() * cart_item.quantity
    ))

db.session.add(order)
db.session.commit()

# Clear cart
CartItem.query.filter_by(user_id=user_id).delete()
db.session.commit()
```

---

### Update Order Status

```python
from models import Order
from datetime import datetime

order = Order.query.get(order_id)

# Update status
order.status = 'shipped'  # pending, confirmed, processing, shipped, delivered, cancelled
order.tracking_number = 'TRK-12345'
order.shipped_at = datetime.utcnow()

db.session.commit()
```

---

### Get User's Orders

```python
from models import Order

# All orders (newest first)
orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()

# Filter by status
pending = Order.query.filter_by(user_id=user_id, status='pending').all()
shipped = Order.query.filter_by(user_id=user_id, status='shipped').all()

# Get totals
total_spent = sum(o.total_amount for o in orders)
order_count = len(orders)
```

---

### Get Order Details

```python
from models import Order

order = Order.query.get(order_id)

# Access order data
print(f"Order: {order.order_number}")
print(f"Status: {order.status} (badge: {order.get_status_badge()})")
print(f"Payment: {order.payment_status} (badge: {order.get_payment_badge()})")
print(f"Total: GH₵{order.total_amount:.2f}")
print(f"Items: {len(order.order_items)}")

# Iterate items
for item in order.order_items:
    print(f"  - {item.product_name} x{item.quantity} @ GH₵{item.unit_price:.2f}")
```

---

### Verify Email Before Checkout

```python
# In route
if not current_user.is_verified:
    flash('Please verify your email before checkout')
    return redirect(url_for('cart'))
```

---

## API Responses

### Place Order (POST /checkout)

**Success Response (200):**
```json
{
    "success": true,
    "message": "Order placed successfully",
    "order_id": 1,
    "order_number": "ORD-20251128051626"
}
```

**Error Response (400):**
```json
{
    "success": false,
    "message": "phone is required"
}
```

---

### Cancel Order (POST /account/order/<id>/cancel)

**Success Response (200):**
```json
{
    "success": true,
    "message": "Order cancelled successfully"
}
```

**Error Response (400):**
```json
{
    "success": false,
    "message": "Cannot cancel order in shipped status"
}
```

---

### Submit Review (POST /account/order/<id>/review)

**Request Body:**
```json
{
    "rating": 5,
    "comment": "Great product, fast delivery!"
}
```

**Success Response (200):**
```json
{
    "success": true,
    "message": "Review submitted successfully"
}
```

---

## Template Variables

### Cart Template (`cart.html`)
- `cart_items`: List of CartItem objects
- `total`: Float, cart total
- `current_user`: User object

### Checkout Template (`checkout.html`)
- `cart_items`: List of CartItem objects
- `subtotal`: Float
- `shipping_cost`: Float
- `tax`: Float
- `total`: Float
- `current_user`: User object

### Confirmation Template (`order_confirmation.html`)
- `order`: Order object
- `recommended_products`: List of Product objects

### History Template (`order_history.html`)
- `orders`: List of Order objects ordered by date DESC

### Detail Template (`order_detail.html`)
- `order`: Order object

---

## Status Badge Colors

| Status | Badge Class | Color |
|--------|------------|-------|
| pending | warning | Yellow |
| confirmed | info | Light Blue |
| processing | primary | Blue |
| shipped | secondary | Gray |
| delivered | success | Green |
| cancelled | danger | Red |

| Payment | Badge Class | Color |
|---------|------------|-------|
| unpaid | warning | Yellow |
| paid | success | Green |
| failed | danger | Red |
| refunded | secondary | Gray |

---

## Database Queries

### Get All Orders with Items
```python
Order.query.options(db.joinedload(Order.order_items)).all()
```

### Get Orders by Date Range
```python
from datetime import datetime, timedelta

start_date = datetime.now() - timedelta(days=7)
orders = Order.query.filter(Order.created_at >= start_date).all()
```

### Get Top Spending Customers
```python
from sqlalchemy import func

top_customers = db.session.query(
    User, 
    func.sum(Order.total_amount).label('total')
).join(Order).group_by(User.id).order_by(func.sum(Order.total_amount).desc()).limit(10).all()
```

---

## Testing

### Run All Tests
```bash
cd e:\python_projects\digialhome
E:/python_projects/digialhome/venv/Scripts/python.exe test_order_system.py
E:/python_projects/digialhome/venv/Scripts/python.exe test_order_flow.py
```

### Run Flask App
```bash
cd e:\python_projects\digialhome
E:/python_projects/digialhome/venv/Scripts/python.exe run.py
```

### Initialize Database
```bash
cd e:\python_projects\digialhome
E:/python_projects/digialhome/venv/Scripts/python.exe init_db_fresh.py
```

---

## Important Notes

1. **Email Verification Required**: Users must verify email before checkout
2. **Order Numbers**: Generated as ORD-YYYYMMDDHHMMSS (unique per second)
3. **Pricing**: 5% tax is calculated on subtotal
4. **Shipping**: Fixed at GH₵10.00 (can be made configurable)
5. **Stock Validation**: Checked during cart operations, not order placement
6. **Product Snapshots**: OrderItem stores product name and price at purchase time

---

## Frontend Events

### Cart Page
- `updateQuantity()`: AJAX call on quantity change
- `removeItem()`: Removes from cart via server
- `clearCart()`: Empties cart with confirmation

### Checkout Page
- `submitCheckout()`: Validates and submits form
- Form validation on phone, address, etc.

### Order History
- `filterOrders(status)`: Client-side filtering
- `cancelOrder()`: Cancels pending orders
- `leaveReview()`: Opens review modal

---

## Common Issues & Solutions

### Issue: "Table cart_item has no column named updated_at"
**Solution:** Run `init_db_fresh.py` to reinitialize database

### Issue: Duplicate backref error on startup
**Solution:** Already fixed in current models.py - relationships use backref on User side only

### Issue: Orders not showing in history
**Solution:** Ensure user_id is correctly set and order is committed to database

### Issue: Checkout returns 403 Unauthorized
**Solution:** Verify current_user is logged in and email is verified (is_verified=True)

---

## Environment Variables

```
FLASK_ENV=production
FLASK_APP=app.py
UPLOAD_FOLDER=static/uploads
DATABASE_URL=sqlite:///instance/digitalhome.db
```

---

## File Sizes

- models.py: ~400 lines (Order + OrderItem + CartItem)
- app.py: +250 lines (new routes)
- cart.html: ~280 lines
- checkout.html: ~270 lines
- order_confirmation.html: ~280 lines
- order_history.html: ~280 lines
- order_detail.html: ~320 lines

**Total New Code:** ~2000 lines

---

## Next Steps

1. **Integration**
   - [ ] Connect payment gateway
   - [ ] Enable email notifications
   - [ ] Setup SMS alerts

2. **Enhancement**
   - [ ] Add order export (PDF/CSV)
   - [ ] Implement refund system
   - [ ] Add order fulfillment workflow

3. **Testing**
   - [ ] Load testing with concurrent orders
   - [ ] Payment gateway integration testing
   - [ ] Email delivery verification

---

## Support

For issues or questions, check:
1. ORDER_SYSTEM_COMPLETE.md - Full documentation
2. test_order_system.py - Model validation
3. test_order_flow.py - Workflow examples
4. Code comments in app.py routes


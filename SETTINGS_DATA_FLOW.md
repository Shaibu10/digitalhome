# How Dynamic Settings Flow Through the System

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATABASE                                 │
│ ┌───────────────────────────────────────────────────────────┐   │
│ │ SystemSettings Table                                      │   │
│ │ - standard_shipping_cost = 10.00                          │   │
│ │ - express_shipping_cost = 15.00                           │   │
│ │ - free_shipping_threshold = 100.00                        │   │
│ │ - tax_rate = 0.05 (5%)                                    │   │
│ │ - updated_at = 2024-01-15 14:30:00                        │   │
│ │ - updated_by_id = 1 (admin)                               │   │
│ └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
          ▲                           ▲
          │                           │
    (Admin Updates)             (Checkout Reads)
          │                           │
          ▼                           ▼
┌──────────────────┐      ┌────────────────────────┐
│  Admin Panel     │      │  Checkout Process      │
│  /admin/settings │      │  /checkout (GET/POST)  │
│                  │      │                        │
│ ✓ Update costs   │      │ ✓ Read settings        │
│ ✓ Update tax     │      │ ✓ Calculate totals     │
│ ✓ Save to DB     │      │ ✓ Display options      │
│ ✓ Log changes    │      │ ✓ Apply to orders      │
└──────────────────┘      └────────────────────────┘
```

## Checkout Flow with Dynamic Settings

### Step 1: Checkout Page Load (GET Request)

**URL:** `/checkout`

```
1. User navigates to checkout
2. Flask app loads checkout() function
3. Code: settings = SystemSettings.get_settings()
4. Database returns: tax_rate = 0.05, standard_shipping_cost = 10.00, etc.
5. Code: shipping_options = calculate_shipping_cost(subtotal, cart_items)
6. Function reads settings values and creates dynamic options:
   - Free Shipping (5-7 days) - if subtotal >= 100
   - Standard Shipping (3-5 days) - GH₵ 10.00
   - Express Shipping (1-2 days) - GH₵ 15.00
7. Code: tax = subtotal * settings.tax_rate
8. Example: tax = 100 * 0.05 = GH₵ 5.00
9. Template receives all values
10. HTML renders: "Tax (5%):" with dynamic tax_rate variable
11. User sees checkout form with current prices
```

**Database Call Stack:**
```python
checkout() @ Line 656
  ├─ SystemSettings.get_settings()  # Query 1: Fetch current settings
  │  └─ SELECT * FROM system_settings LIMIT 1
  │     Result: {tax_rate: 0.05, standard_shipping_cost: 10.00, ...}
  │
  ├─ calculate_shipping_cost(subtotal, cart_items)  # Query 2: Called within
  │  └─ settings = SystemSettings.get_settings()
  │     (Cached in memory, no 2nd DB call)
  │
  └─ render_template('checkout.html', tax_rate=..., tax=...)
     └─ Template displays with dynamic values
```

**Example Output to Template:**
```python
{
    'subtotal': 100.00,
    'shipping_cost': 10.00,  # If standard selected
    'tax': 5.00,  # 100 * 0.05
    'tax_rate': 5.0,  # For display: "Tax (5%):"
    'total': 115.00,  # 100 + 10 + 5
    'shipping_options': {
        'free': {'label': 'Free Shipping (5-7 days)', 'cost': 0.00},
        'standard': {'label': 'Standard Shipping (3-5 days) - GH₵ 10.00', 'cost': 10.00},
        'express': {'label': 'Express Shipping (1-2 days) - GH₵ 15.00', 'cost': 15.00}
    }
}
```

### Step 2: Customer Sees Options

**Checkout Template Rendering:**

```html
<!-- Order Summary Section -->
Order Total Calculation:
  Subtotal: GH₵ 100.00
  Shipping: GH₵ 10.00 (standard - read from settings)
  Tax (5%): GH₵ 5.00 (5% = tax_rate from settings)
  ────────────────────
  Total: GH₵ 115.00

<!-- Shipping Method Options (Dynamic) -->
Radio Buttons:
  ☐ Free Shipping (5-7 days)           [Cost: GH₵ 0.00]
  ⊙ Standard Shipping (3-5 days) - GH₵ 10.00  [Selected]
  ☐ Express Shipping (1-2 days) - GH₵ 15.00

Note: Prices shown are from database,
      not hardcoded in template!
```

### Step 3: Customer Places Order (POST Request)

**URL:** `/checkout` (POST)

```
1. User fills shipping form
2. User selects shipping method: 'standard'
3. User selects payment method: 'cod'
4. User clicks "Place Order"
5. JavaScript sends POST request with JSON data

Request Data:
{
    'first_name': 'John',
    'last_name': 'Doe',
    'shipping_method': 'standard',
    'payment_method': 'cod',
    ...other fields...
}

6. Flask checkout() POST handler receives request
7. Code: settings = SystemSettings.get_settings()
8. Database returns current settings (again)
9. Code: shipping_cost = shipping_options[selected_shipping]['cost']
10. Code: tax = subtotal * settings.tax_rate
11. Order created with dynamic values:
    - shipping_method: 'standard'
    - shipping_cost: 10.00  (from settings at order time)
    - tax applied: 5.00     (using current tax_rate)
    - total_amount: 115.00  (100 + 10 + 5)
```

**Database Calls (POST):**
```python
checkout() POST @ Line 689
  ├─ CartItem.query.filter_by(user_id=...).all()  # Get items
  │
  ├─ SystemSettings.get_settings()  # Query: Fetch settings
  │  └─ SELECT * FROM system_settings LIMIT 1
  │     Result: {tax_rate: 0.05, standard_shipping_cost: 10.00, ...}
  │
  ├─ calculate_shipping_cost(subtotal, cart_items)
  │  └─ settings = SystemSettings.get_settings()
  │     (Cached, no new DB call)
  │
  ├─ Create Order object with calculated values
  │
  ├─ db.session.add(order)  # SQL INSERT
  │  └─ INSERT INTO order (user_id, total_amount, tax, shipping_cost, ...)
  │
  ├─ db.session.commit()  # Save to database
  │
  └─ CartItem.query.filter_by(user_id=...).delete()  # Clear cart
```

### Step 4: Order Stored with Current Settings

**Database Result:**
```sql
INSERT INTO order (
    user_id=1,
    order_number='ORD-20240115143000',
    subtotal=100.00,
    shipping_cost=10.00,  ← Captures value at order time
    tax_amount=5.00,      ← Captures calculation at order time
    total_amount=115.00,
    payment_method='cod',
    shipping_method='standard',
    status='pending',
    created_at='2024-01-15 14:30:00'
);
```

**Important:** Order stores the actual values used, not references to settings. If admin changes settings later, existing orders are unaffected.

## Setting Change Propagation

### Scenario: Admin Changes Shipping Cost

**Time: 2:30 PM**
- Settings: Standard Shipping = GH₵ 10.00
- Customer A orders: Pays GH₵ 10.00 shipping

**Time: 3:00 PM (Admin updates)**
- Admin changes: Standard Shipping = GH₵ 12.00
- Database update: `UPDATE system_settings SET standard_shipping_cost=12.00`
- Activity log: `Admin 'john' updated shipping settings at 3:00 PM`

**Time: 3:15 PM**
- Customer B loads checkout
- System: `SELECT * FROM system_settings`
- Gets: standard_shipping_cost = 12.00
- Customer B pays GH₵ 12.00 shipping

**Important:** Customer A's order still shows GH₵ 10.00 (locked in at order time)

## Code Flow Diagram

```
User navigates to /checkout (GET)
  │
  ├─ @login_required: Verify logged in
  ├─ Check: User email verified
  ├─ Check: Cart not empty
  │
  ├─ Query database:
  │  SystemSettings.get_settings()
  │  └─ Returns: tax_rate=0.05, standard_shipping_cost=10.00, ...
  │
  ├─ Calculate subtotal from cart items
  │
  ├─ Call calculate_shipping_cost(subtotal, cart_items)
  │  └─ Reads: settings.standard_shipping_cost
  │  └─ Reads: settings.express_shipping_cost
  │  └─ Reads: settings.free_shipping_threshold
  │  └─ Returns: {'free': {...}, 'standard': {...}, 'express': {...}}
  │
  ├─ Calculate: tax = subtotal * settings.tax_rate
  │  └─ Example: 100 * 0.05 = 5.00
  │
  ├─ Select default shipping: min cost option
  │  └─ shipping_cost = shipping_options[default_method]['cost']
  │
  ├─ Calculate: total = subtotal + shipping_cost + tax
  │  └─ Example: 100 + 10 + 5 = 115
  │
  └─ render_template('checkout.html',
     subtotal=100,
     shipping_cost=10,
     tax=5,
     tax_rate=5.0,  ← For display: "Tax (5%):"
     total=115,
     shipping_options={...}
   )
```

## Performance Considerations

### Database Optimization

```python
# Current implementation (Optimized)
settings = SystemSettings.get_settings()  # 1 query
tax = subtotal * settings.tax_rate        # Use in memory
shipping = calculate_shipping_cost(...)   # Reuses same object
# Total: 1 DB query per request ✓

# Previously (If hardcoded)
tax = subtotal * 0.05  # 0 queries, but inflexible ✗

# If poorly implemented
settings1 = SystemSettings.query.first()  # Query 1
settings2 = SystemSettings.query.first()  # Query 2 (duplicate!)
settings3 = SystemSettings.query.first()  # Query 3 (duplicate!)
# Total: 3 DB queries per request (wasteful) ✗
```

### Caching Strategy (Current)
```
Per Request Caching:
  Each checkout request gets settings once
  Multiple calculations reuse same object
  No redundant database calls
```

### Future Enhancement (Recommended)
```
If high traffic:
  ├─ Cache settings in application memory
  ├─ Invalidate on admin update
  ├─ Reduces DB calls to near-zero
  └─ Typical cache hit rate: 95%+
```

## Testing the Flow

### Test 1: Basic Checkout with Dynamic Settings

```python
def test_checkout_dynamic_settings():
    # Create test user and cart
    user = create_test_user()
    add_to_cart(user, product, quantity=1)
    
    # Verify default settings
    settings = SystemSettings.get_settings()
    assert settings.tax_rate == 0.05
    assert settings.standard_shipping_cost == 10.00
    
    # Make GET request to checkout
    response = client.get('/checkout', auth=user)
    assert response.status_code == 200
    
    # Verify template received correct values
    assert b'Tax (5%)' in response.data  # Dynamic
    assert b'10.00' in response.data     # Dynamic
    
    print("✓ Test passed: Dynamic settings in checkout")
```

### Test 2: Settings Persist to Orders

```python
def test_settings_saved_to_order():
    # Place order with current settings
    order = place_order(user, shipping_method='standard')
    
    # Admin changes settings
    settings = SystemSettings.get_settings()
    settings.standard_shipping_cost = 20.00
    db.session.commit()
    
    # Verify order still has old value
    assert order.shipping_cost == 10.00  # Original
    
    # New orders use new settings
    order2 = place_order(user2, shipping_method='standard')
    assert order2.shipping_cost == 20.00  # Updated
    
    print("✓ Test passed: Settings changes don't affect existing orders")
```

## Summary

### Data Flow
1. Admin updates settings → Database updated
2. Customer loads checkout → Reads current settings
3. Customer places order → Settings values frozen in order
4. Settings change → Only affects future orders

### Key Points
- ✓ Settings are dynamic (not hardcoded)
- ✓ Changes take effect immediately for new orders
- ✓ Existing orders preserve original pricing
- ✓ Minimal database queries (1 per request)
- ✓ Audit trail tracks all changes
- ✓ Admin controls without code changes

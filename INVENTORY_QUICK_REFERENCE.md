# Inventory Management - Quick Reference

## When Inventory is Deducted

**✓ DEDUCTED** when:
- Payment is successfully verified (`payment_status = 'paid'`)
- Happens in `/verify/<reference>` route
- Happens in `/webhook` when `charge.success` event received

## When Inventory is Restored

**✓ RESTORED** when:
- Order is cancelled (`/cancel_order` route)
- Payment is refunded (`/api/update_order_status` with `payment_status = 'refunded'`)

## Related Methods

### Order.deduct_inventory()
```python
success, message = order.deduct_inventory()
# Returns: (True, "Inventory deducted successfully")
# Or: (False, "Insufficient stock for Product Name...")
```

### Order.restore_inventory()
```python
success, message = order.restore_inventory()
# Returns: (True, "Inventory restored successfully")
# Or: (False, "Error restoring inventory: ...")
```

## Affected Routes

| Route | Method | Effect |
|---|---|---|
| `/payment/verify/<ref>` | GET | Deducts inventory when payment verified |
| `/payment/webhook` | POST | Deducts inventory on charge.success |
| `/cancel_order` | POST | Restores inventory when order cancelled |
| `/api/update_order_status` | POST | Restores inventory when marked refunded |

## Order States and Inventory

```
Order Placed
  ↓ (Status: pending, Payment: unpaid)
  ✗ Inventory NOT deducted
  
Customer Pays
  ↓ (Status: confirmed, Payment: paid)
  ✓ Inventory DEDUCTED here
  
Order Cancelled
  ✓ Inventory RESTORED here
  
Order Refunded
  ✓ Inventory RESTORED here
```

## Error Scenarios

| Error | Cause | Resolution |
|---|---|---|
| "Insufficient stock" | Stock changed after order placed | Cancel order, customer reorders |
| "Product not found" | Product deleted | Manual admin inventory adjustment |
| Deduction fails | Database error | Check logs, retry payment verification |

## Testing Commands

```python
# Check product stock
from models import Product
p = Product.query.get(1)
print(f"Stock: {p.stock_quantity}")

# Create test order
from models import Order, OrderItem
order = Order.query.get(1)
success, msg = order.deduct_inventory()
print(f"Result: {success} - {msg}")

# Restore inventory
success, msg = order.restore_inventory()
print(f"Result: {success} - {msg}")
```

---

**Remember**: Inventory is only deducted when `payment_status = 'paid'`, not at checkout!


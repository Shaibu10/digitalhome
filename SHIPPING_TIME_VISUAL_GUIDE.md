# Shipping Time Feature - Visual Reference

## Admin Settings Page Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                     SYSTEM SETTINGS                              │
├─────────────────────────────────────────────────────────────────┤
│ [Shipping Settings] [Tax Settings]                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  SHIPPING COST CONFIGURATION                                     │
│  ─────────────────────────────────                               │
│  Standard Shipping Cost:    [10.00]  GH₵                         │
│  Express Shipping Cost:     [15.00]  GH₵                         │
│  Free Shipping Threshold:   [100.00] GH₵                         │
│                                                                   │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                                                   │
│  DELIVERY TIME (Days, Hours, Minutes)  ← NEW!                    │
│  ─────────────────────────────────────                           │
│                                                                   │
│  Standard Shipping                                               │
│  From: [3] days [0] hrs [0] min                                 │
│  To:   [5] days [2] hrs [30] min                                │
│                                                                   │
│  Express Shipping                                                │
│  From: [1] day  [8] hrs [0] min                                 │
│  To:   [2] days [18] hrs [0] min                                │
│                                                                   │
│  Free Shipping                                                   │
│  From: [5] days [0] hrs [0] min                                 │
│  To:   [7] days [12] hrs [0] min                                │
│                                                                   │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                                                   │
│  SHIPPING OPTIONS SUMMARY  ← LIVE PREVIEW                        │
│  • Free Shipping: ≥ GH₵ 100.00 (5-7d 0h0m - 12h0m)             │
│  • Standard Shipping: GH₵ 10.00 (3-5d 0h0m - 2h30m)            │
│  • Express Shipping: GH₵ 15.00 (1-2d 8h0m - 18h0m)             │
│                                                                   │
│  [Save Shipping Settings] [Reset]                                │
│                                                                   │
│  Last updated: 2025-12-06 14:30:45 by admin                     │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Form Fields Breakdown

### Standard Shipping Section
```
┌─ STANDARD SHIPPING ─────────────────────────────────────────┐
│                                                               │
│ From:                                                        │
│  [3]         [0]         [0]         [5]                    │
│  Days        Hours       Minutes      (hidden: max days)     │
│                                                               │
│ To:                                                          │
│  [5]         [2]         [30]        (labels below)          │
│  Days        Hours       Minutes                             │
│                                                               │
│ Display: "3-5d 0h0m - 2h30m"                               │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Input Validation Rules

```
┌──────────────────┬────────────────┬────────────────────┐
│  Field Type      │  Min Value     │  Max Value         │
├──────────────────┼────────────────┼────────────────────┤
│  Days            │  0             │  30                │
│  Hours           │  0             │  23                │
│  Minutes         │  0             │  59                │
└──────────────────┴────────────────┴────────────────────┘
```

## Example Configurations

### Configuration 1: Standard with Precise Hours
```
Standard Shipping:
  From: 3d 0h 0m   → Delivery starts on 3rd day
  To:   5d 2h 30m  → Delivery ends on 5th day at 2:30 AM

Display: "Delivery: 3-5 days (0-2 hours 30 minutes)"
```

### Configuration 2: Express Overnight
```
Express Shipping:
  From: 0d 8h 0m   → Delivery starts in 8 hours
  To:   1d 18h 0m  → Delivery ends at 6 PM next day

Display: "Delivery: 8 hours - 1 day 6 PM"
```

### Configuration 3: Free Shipping Delayed
```
Free Shipping (≥ GH₵100):
  From: 5d 0h 0m   → Delivery starts on 5th day
  To:   7d 12h 0m  → Delivery ends on 7th day at noon

Display: "Delivery: 5-7 days (free shipping)"
```

## JavaScript Real-Time Update

When admin changes any time field:

```
BEFORE: "3-5d 0h0m - 0h0m"
↓ (Admin changes max hours from 0 to 2)
DURING: "[3] - [5] d  [0] h [0] m - [2] h [30] m"
↓ (Admin changes max minutes to 30)
AFTER: "3-5d 0h0m - 2h30m"  ← Updates in preview
```

## Database Storage Format

```
SystemSettings Table Row:
┌────────────────────────────────────────────┐
│ standard_shipping_days_min:      3         │
│ standard_shipping_days_max:      5         │
│ standard_shipping_hours_min:     0         │
│ standard_shipping_hours_max:     2         │
│ standard_shipping_minutes_min:   0         │
│ standard_shipping_minutes_max:   30        │
├────────────────────────────────────────────┤
│ express_shipping_days_min:       1         │
│ express_shipping_days_max:       2         │
│ express_shipping_hours_min:      8         │
│ express_shipping_hours_max:      18        │
│ express_shipping_minutes_min:    0         │
│ express_shipping_minutes_max:    0         │
├────────────────────────────────────────────┤
│ free_shipping_days_min:          5         │
│ free_shipping_days_max:          7         │
│ free_shipping_hours_min:         0         │
│ free_shipping_hours_max:         12        │
│ free_shipping_minutes_min:       0         │
│ free_shipping_minutes_max:       0         │
└────────────────────────────────────────────┘
```

## API Flow Diagram

```
┌──────────────┐
│ Admin Form   │
│  with Time   │
└──────┬───────┘
       │
       ↓
┌──────────────────────────────────┐
│ Form Submission to /admin/settings│
└──────┬───────────────────────────┘
       │
       ↓
┌──────────────────────────────────┐
│ app.py: admin_settings() route    │
│  - Extract hour/minute inputs    │
│  - Validate ranges               │
│  - Convert to integers           │
└──────┬───────────────────────────┘
       │
       ↓
┌──────────────────────────────────┐
│ SystemSettings.update_shipping_  │
│ settings() method                │
│  - Update all 12 columns         │
│  - Set updated_by_id             │
│  - Commit to database            │
└──────┬───────────────────────────┘
       │
       ↓
┌──────────────────────────────────┐
│ Database Updated                 │
│ ✓ All records saved              │
│ ✓ Activity logged                │
└──────────────────────────────────┘
```

## Feature Comparison

### Before Implementation
```
Shipping Settings:
├── Shipping Costs (GH₵)
├── Delivery Days (min-max)
└── Free Shipping Threshold
```

### After Implementation
```
Shipping Settings:
├── Shipping Costs (GH₵)
├── Delivery Days (min-max)
├── Delivery Hours (min-max) ← NEW
├── Delivery Minutes (min-max) ← NEW
└── Free Shipping Threshold
```

## Time Display Examples in UI

```
Summary Display Format:
"5-7d 0h0m - 12h0m"  
 │  │  │ │  │ │ 
 │  │  │ │  │ └─ Max minutes
 │  │  │ │  └──── Max hours
 │  │  │ └─────── From/To separator
 │  │  └──────── Min minutes
 │  └─────────── Min hours
 └──────────────── Days (min-max)
```

## Responsive Layout

```
Desktop (≥ 992px):
┌─ From ──────────────┬─ To ──────────────┐
│ [d] [h] [m] │ [d] [h] [m] │
└─────────────────────────────────────────┘

Tablet (768px - 991px):
┌─ From ──────────────┐
│ [d] [h] [m]         │
├─ To ────────────────┤
│ [d] [h] [m]         │
└─────────────────────┘

Mobile (< 768px):
┌─────────────────────┐
│ [d] [h] [m]         │
├─────────────────────┤
│ [d] [h] [m]         │
└─────────────────────┘
```

---

**Document Created:** December 6, 2025
**Feature Status:** Ready for Production ✓

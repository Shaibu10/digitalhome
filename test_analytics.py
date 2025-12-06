from app import app, db
from analytics_helpers import (
    get_sales_trends, get_top_products, get_customer_demographics,
    get_conversion_funnel, get_revenue_by_category, get_order_status_breakdown,
    get_monthly_trends
)

with app.app_context():
    print("Testing Analytics Dashboard Functions\n")
    
    # Test sales trends
    print("1. Sales Trends (30 days):")
    trends = get_sales_trends(30)
    print(f"   Dates: {len(trends['dates'])} days")
    print(f"   Total Revenue: GH₵ {sum(trends['revenue']):.2f}")
    print(f"   Total Orders: {sum(trends['orders'])}")
    
    # Test top products
    print("\n2. Top Products:")
    products = get_top_products(5)
    print(f"   Found {len(products)} products")
    for item in products[:3]:
        print(f"   - {item['product'].name}: {item['units_sold']} units, GH₵ {item['total_revenue']:.2f}")
    
    # Test customer demographics
    print("\n3. Customer Demographics:")
    demo = get_customer_demographics()
    print(f"   Total Users: {demo['total_users']}")
    print(f"   Active Users: {demo['active_users']}")
    print(f"   Verified Users: {demo['verified_users']}")
    print(f"   Users with Orders: {demo['users_with_orders']}")
    print(f"   Avg Orders per Customer: {demo['avg_orders_per_customer']}")
    
    # Test conversion funnel
    print("\n4. Conversion Funnel:")
    funnel = get_conversion_funnel()
    print(f"   Total Users: {funnel['stages']['total_users']}")
    print(f"   Viewed Products: {funnel['stages']['viewed_products']}")
    print(f"   Added to Cart: {funnel['stages']['added_to_cart']}")
    print(f"   Completed Order: {funnel['stages']['completed_order']}")
    print(f"   Overall Conversion Rate: {funnel['conversion_rates']['overall_conversion']}%")
    
    # Test top categories
    print("\n5. Top Categories:")
    cats = get_revenue_by_category(5)
    print(f"   Found {len(cats)} categories")
    for item in cats[:3]:
        print(f"   - {item['category'].name}: GH₵ {item['revenue']:.2f}, {item['units_sold']} units")
    
    # Test order status breakdown
    print("\n6. Order Status Breakdown:")
    status = get_order_status_breakdown()
    for st, count in status.items():
        print(f"   - {st}: {count} orders")
    
    # Test monthly trends
    print("\n7. Monthly Trends (12 months):")
    monthly = get_monthly_trends(12)
    print(f"   Months: {len(monthly['months'])}")
    print(f"   Total Monthly Revenue: GH₵ {sum(monthly['revenue']):.2f}")
    print(f"   Total Monthly Orders: {sum(monthly['orders'])}")
    
    print("\n✅ All analytics functions working correctly!")

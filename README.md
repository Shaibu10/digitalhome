# Digital Home E-Commerce Platform

A full-featured Flask e-commerce platform with:
- **Product Catalog** - Browse, search, filter products by category
- **Shopping Cart** - Add/remove items, manage quantities
- **Checkout** - Shipping options, tax calculation, order review
- **Payment Integration** - Paystack payment gateway
- **Admin Panel** - Manage products, orders, settings, analytics
- **Shipping Management** - Configurable shipping costs with day/hour/minute precision
- **Database Backups** - Create, restore, and download database backups
- **SMS Service** - Send SMS notifications and campaigns
- **Email Verification** - User email verification system
- **Order Management** - View, track, and manage customer orders
- **Analytics Dashboard** - Order statistics and business insights

## Features

### For Customers
- User registration and authentication
- Browse product catalog with filtering
- Add products to cart
- Checkout with multiple shipping options
- Real-time shipping cost calculation
- Payment via Paystack
- Order history and tracking
- Email notifications

### For Admins
- Dashboard with key metrics
- Product management (CRUD)
- Order management and status updates
- User management
- System settings configuration
- Shipping cost and time configuration
- Database backup and restore
- Analytics and reports
- SMS campaign management

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Bootstrap 5, jQuery
- **Payment**: Paystack API
- **SMS**: mNotify API
- **Email**: Gmail API
- **Database Migrations**: Alembic (Flask-Migrate)

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/digialhome.git
cd digialhome
```

2. Create virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize database:
```bash
flask db upgrade
```

5. Create admin user:
```bash
python -c "from app import app, db; from models import User; \
app.app_context().push(); \
user = User(username='admin', email='admin@example.com', is_admin=True); \
user.set_password('admin123'); \
db.session.add(user); \
db.session.commit(); \
print('Admin user created')"
```

6. Run the application:
```bash
python run.py
```

Visit `http://localhost:5000` in your browser.

## Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///instance/digitalhome.db
PAYSTACK_PUBLIC_KEY=your-paystack-public-key
PAYSTACK_SECRET_KEY=your-paystack-secret-key
MNOTIFY_API_KEY=your-mnotify-api-key
```

### Admin Login
- **Email**: admin@example.com
- **Password**: admin123

## Project Structure

```
digialhome/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── models.py                 # Database models
├── extensions.py             # Flask extensions
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
├── backup_utils.py           # Backup and restore utilities
├── backup_cli.py             # Command-line backup tool
├── instance/
│   └── digitalhome.db        # SQLite database
├── templates/
│   ├── base.html             # Base template
│   ├── admin/                # Admin templates
│   │   ├── backups.html      # Backup management
│   │   ├── dashboard.html
│   │   ├── products.html
│   │   ├── orders.html
│   │   └── settings.html
│   └── ...
├── static/
│   ├── css/                  # Stylesheets
│   ├── js/                   # JavaScript files
│   └── images/               # Image assets
├── migrations/               # Database migrations
└── backups/                  # Database backups directory
```

## Database Backup & Restore

### Create Backup
```bash
python backup_cli.py create -d "Backup description"
```

### List Backups
```bash
python backup_cli.py list -v
```

### Restore Backup
```bash
python backup_cli.py restore digitalhome_backup_20251206_064300.db
```

### Verify Backup
```bash
python backup_cli.py verify digitalhome_backup_20251206_064300.db
```

Or use the web interface at `/admin/backups`

## API Endpoints

### Backup Management
- `POST /api/backup/create` - Create new backup
- `GET /api/backup/list` - List all backups
- `POST /api/backup/restore` - Restore from backup
- `POST /api/backup/delete` - Delete backup
- `GET /api/backup/download/<filename>` - Download backup

### Shopping
- `POST /add_to_cart` - Add item to cart
- `POST /remove_from_cart` - Remove item from cart
- `GET /cart` - View cart
- `POST /checkout` - Process checkout

### Orders
- `POST /api/calculate-checkout` - Calculate shipping and totals

## Shipping Configuration

Configure shipping methods in Admin Panel → System Settings:

- **Free Shipping**: Set threshold amount
- **Standard Shipping**: Days, hours, minutes, cost
- **Express Shipping**: Days, hours, minutes, cost

Format: "DDd HHhMMm - DDd HHhMMm" (e.g., "3d 00h00m - 5d 02h30m")

## Testing

Run the test suite:
```bash
python test_backup_restore.py
python test_download.py
python test_restore.py
```

## Development

### Create New Database Migration
```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

### Run Tests
```bash
pytest tests/
```

## Deployment

For production deployment:

1. Set environment variables in `.env`:
   - Set `FLASK_ENV=production`
   - Generate strong `SECRET_KEY`
   - Configure database path

2. Use production WSGI server:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

3. Set up reverse proxy (Nginx/Apache) for HTTPS

4. Create regular database backups

5. Enable logging and monitoring

## Production Readiness

✓ Database schema finalized with 22 tables  
✓ Shipping time feature fully implemented  
✓ Real-time order calculation via AJAX  
✓ Admin backup and restore system  
✓ Security validations and access controls  
✓ Error handling and logging  
✓ All core features tested and verified  

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email support@digitalhome.com or open an issue on GitHub.

## Changelog

### Version 1.0.0 (December 6, 2025)
- Initial release
- Full e-commerce functionality
- Shipping time configuration with day/hour/minute precision
- Database backup and restore system
- Admin dashboard and settings
- Payment integration with Paystack
- SMS notifications
- Email verification

---

**Author**: Digital Home Development Team  
**Last Updated**: December 6, 2025

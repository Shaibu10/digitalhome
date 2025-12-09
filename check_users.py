from app import create_app, db, User

app = create_app()
with app.app_context():
    users = User.query.all()
    print(f'\nTotal users: {len(users)}')
    for u in users:
        print(f'  - {u.email} (phone: {u.phone_number}, verified: {u.is_verified})')

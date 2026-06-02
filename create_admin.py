from app import app
from models import db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    admin = User(
        username='admin',
        email='admin@gmail.com',
        password=generate_password_hash('admin123'),
        is_admin=True
    )
    db.session.add(admin)
    db.session.commit()
    print('Admin created successfully!')
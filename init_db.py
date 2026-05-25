from app import create_app, db
from app.models import User
from app import bcrypt

app = create_app()
with app.app_context():
    db.create_all()
    # Örnek bir yönetici hesabı ekleyelim
    admin_exists = User.query.filter_by(email='admin@site.com').first()
    if not admin_exists:
        hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin = User(name='Yönetici Ahmet', email='admin@site.com', password_hash=hashed_pw, role='manager', apartment_no='Blok A - D1')
        db.session.add(admin)
        db.session.commit()
        print("Veritabanı başarıyla oluşturuldu ve örnek yönetici hesabı eklendi! (admin@site.com / admin123)")

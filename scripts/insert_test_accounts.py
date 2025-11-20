from app import create_app
from models import db, User
from flask import Flask

def insert_test_account() -> None:
    app: Flask = create_app()
    with app.app_context():
        print('Inserting a test account...')

        # Ajouter un compte administrateur simple
        admin: User = User(email='admin@test.com', name='Admin', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)

        db.session.commit()
        print('Test account inserted successfully.')

if __name__ == '__main__':
    insert_test_account()
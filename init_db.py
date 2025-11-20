#!/usr/bin/env python
"""Initialize the database"""

from app import create_app
from models import db, User, Classe

app = create_app()

with app.app_context():
    # Drop all and recreate
    db.drop_all()
    db.create_all()
    
    # Create admin user
    admin = User(email='admin@ecole.local', name='Admin', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)
    
    # Create some classes
    for class_name in ['6ème', '5ème', '4ème']:
        classe = Classe(name=class_name)
        db.session.add(classe)
    
    db.session.commit()
    print("✅ Base de données initialisée")
    print("   Admin: admin@ecole.local / admin123")

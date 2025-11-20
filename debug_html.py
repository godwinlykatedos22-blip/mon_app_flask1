"""
Debug : Afficher le HTML généré
"""

import sys
sys.path.insert(0, '.')

from app import create_app
from models import db, User, Student, Classe

app = create_app()
app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['WTF_CSRF_ENABLED'] = False

with app.app_context():
    db.create_all()
    admin = User(email='admin@test.com', name='Admin', role='admin')
    admin.set_password('test123')
    db.session.add(admin)
    db.session.commit()
    
    # Vérifier si la classe existe
    sixeme = Classe.query.filter_by(name='6ème').first()
    if not sixeme:
        sixeme = Classe(name='6ème')
        db.session.add(sixeme)
        db.session.commit()
    
    # Vérifier si l'étudiant existe
    student = Student.query.filter_by(first_name='Jean', last_name='Dupont').first()
    if not student:
        student = Student(first_name='Jean', last_name='Dupont', class_id=sixeme.id)
        db.session.add(student)
        db.session.commit()

with app.test_client() as client:
    client.post('/auth/login', data={'email': 'admin@test.com', 'password': 'test123'}, follow_redirects=True)
    response = client.get('/eleves/')
    
    # Trouver les symboles
    html = response.data.decode('utf-8')
    
    # Chercher le tableau
    if '<table' in html:
        print("✅ Tableau trouvé")
        
        # Chercher les lignes d'étudiants
        if 'Dupont' in html:
            print("✅ Étudiant trouvé")
        
        # Chercher les symboles
        if '👁️' in html:
            print("✅ Symbole 👁️ trouvé")
        else:
            print("❌ Symbole 👁️ NOT trouvé")
        
        if '✏️' in html:
            print("✅ Symbole ✏️ trouvé")
        else:
            print("❌ Symbole ✏️ NOT trouvé")
        
        if '🗑️' in html:
            print("✅ Symbole 🗑️ trouvé")
        else:
            print("❌ Symbole 🗑️ NOT trouvé")
        
        # Afficher un aperçu du tableau
        import re
        table_match = re.search(r'<table.*?</table>', html, re.DOTALL)
        if table_match:
            table_html = table_match.group(0)
            # Afficher les 500 premiers caractères
            print("\nAperçu du tableau (500 chars):")
            print(table_html[:500])
    else:
        print("❌ Tableau NOT trouvé")
        print("\nHTML complet:")
        print(html[:1000])

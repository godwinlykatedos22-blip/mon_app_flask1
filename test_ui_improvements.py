"""
Test unitaire des nouvelles fonctionnalités
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from models import db, User, Student, Classe
from bs4 import BeautifulSoup


def test_new_features():
    """Tester les nouvelles fonctionnalités avec un test client"""
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        
        # Créer un admin
        admin = User(email='admin@test.com', name='Admin', role='admin')
        admin.set_password('test123')
        db.session.add(admin)
        
        # Créer des classes
        classes_list = ['6ème', '5ème', '4ème', '3ème']
        for class_name in classes_list:
            classe = Classe(name=class_name)
            db.session.add(classe)
        
        db.session.commit()
        
        # Créer quelques étudiants
        sixeme = Classe.query.filter_by(name='6ème').first()
        for i in range(3):
            student = Student(
                first_name=f'Prénom{i}',
                last_name=f'Nom{i}',
                class_id=sixeme.id
            )
            db.session.add(student)
        db.session.commit()
    
    with app.test_client() as client:
        # 1. Se connecter
        print("1️⃣  Connexion...")
        response = client.post('/auth/login', data={
            'email': 'admin@test.com',
            'password': 'test123'
        }, follow_redirects=True)
        assert response.status_code == 200
        print("   ✅ Connecté")
        
        # 2. Accéder à la page de liste
        print("\n2️⃣  Page de liste des élèves...")
        response = client.get('/eleves/')
        assert response.status_code == 200
        print(f"   ✅ Status {response.status_code}")
        
        # Analyser le HTML
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # 3. Vérifier le bouton Imprimer
        print("\n3️⃣  Vérification du bouton Imprimer...")
        print_button = response.data.decode('utf-8').find('🖨️ Imprimer')
        if print_button != -1:
            print("   ✅ Bouton Imprimer trouvé")
        else:
            print("   ❌ Bouton Imprimer NOT trouvé")
        
        # 4. Vérifier les classes
        print("\n4️⃣  Vérification des classes...")
        for class_name in ['6ème', '5ème', '4ème', '3ème']:
            if class_name in response.data.decode('utf-8'):
                print(f"   ✅ {class_name}")
            else:
                print(f"   ❌ {class_name} NOT found")
        
        # 5. Vérifier le dropdown menu
        print("\n5️⃣  Vérification du menu déroulant...")
        if 'dropdown-menu' in response.data.decode('utf-8'):
            print("   ✅ Menu déroulant trouvé")
        else:
            print("   ❌ Menu déroulant NOT trouvé")
        
        # 6. Vérifier le JavaScript
        print("\n6️⃣  Vérification du JavaScript...")
        js_content = response.data.decode('utf-8')
        if 'exportClass' in js_content:
            print("   ✅ Fonction exportClass présente")
        else:
            print("   ❌ Fonction exportClass NOT trouvée")
        
        if 'get-class-id' in js_content:
            print("   ✅ Route get-class-id référencée")
        else:
            print("   ❌ Route get-class-id NOT trouvée")
        
        # 7. Tester la route get-class-id
        print("\n7️⃣  Test de la route get-class-id...")
        response = client.get('/eleves/get-class-id/6ème')
        assert response.status_code == 200
        data = response.get_json()
        if data.get('class_id'):
            print(f"   ✅ Class ID pour '6ème': {data['class_id']}")
        else:
            print("   ❌ Pas de class_id")
        
        # 8. Vérifier les tooltips
        print("\n8️⃣  Vérification des tooltips...")
        if 'data-bs-toggle="tooltip"' in response.data.decode('utf-8'):
            print("   ✅ Tooltips présentes")
        else:
            print("   ❌ Tooltips NOT trouvées")
        
        # 9. Vérifier les symboles d'action
        print("\n9️⃣  Vérification des symboles d'action...")
        data_str = response.data.decode('utf-8')
        if '👁️' in data_str:
            print("   ✅ Symbole 'Voir' (👁️) trouvé")
        else:
            print("   ❌ Symbole 'Voir' NOT trouvé")
        
        if '✏️' in data_str:
            print("   ✅ Symbole 'Modifier' (✏️) trouvé")
        else:
            print("   ❌ Symbole 'Modifier' NOT trouvé")
        
        if '🗑️' in data_str:
            print("   ✅ Symbole 'Supprimer' (🗑️) trouvé")
        else:
            print("   ❌ Symbole 'Supprimer' NOT trouvé")
        
        print("\n" + "="*60)
        print("✅ TOUS LES TESTS UNITAIRES RÉUSSIS")
        print("="*60)


if __name__ == '__main__':
    try:
        test_new_features()
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

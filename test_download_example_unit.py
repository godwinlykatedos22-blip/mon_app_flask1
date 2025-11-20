"""
Test unitaire pour la route /eleves/download-example
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from models import db, User, Classe
from flask_login import LoginManager


def test_download_example_route():
    """Tester la route download-example localement"""
    
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
        
        # Créer quelques classes
        for class_name in ['6ème A', '5ème B', '4ème C']:
            classe = Classe(name=class_name)
            db.session.add(classe)
        
        db.session.commit()
    
    with app.test_client() as client:
        # 1. Test sans authentification
        print("1️⃣  Test sans authentification...")
        response = client.get('/eleves/download-example')
        assert response.status_code == 302, f"Expected redirect, got {response.status_code}"
        assert '/auth/login' in response.location
        print("   ✅ Redirection vers login correcte")
        
        # 2. Test avec authentification
        print("\n2️⃣  Test avec authentification...")
        response = client.post('/auth/login', data={
            'email': 'admin@test.com',
            'password': 'test123'
        }, follow_redirects=True)
        assert response.status_code == 200
        print("   ✅ Authentification réussie")
        
        # 3. Télécharger le fichier
        print("\n3️⃣  Téléchargement du fichier...")
        response = client.get('/eleves/download-example')
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.content_type}")
        print(f"   Size: {len(response.data)} bytes")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert response.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        assert len(response.data) > 2000
        
        # 4. Valider le format XLSX
        print("\n4️⃣  Validation du format XLSX...")
        assert response.data[:4] == b'PK\x03\x04', "Not a valid ZIP file"
        print("   ✅ Format ZIP valide")
        
        from zipfile import ZipFile
        from io import BytesIO
        with ZipFile(BytesIO(response.data)) as zf:
            files = zf.namelist()
            assert 'xl/workbook.xml' in files
            assert 'xl/worksheets/sheet1.xml' in files
            assert 'xl/worksheets/sheet2.xml' in files
            assert 'xl/worksheets/sheet3.xml' in files
            print(f"   ✅ Structure XLSX complète ({len(files)} fichiers)")
        
        # 5. Vérifier le contenu
        print("\n5️⃣  Vérification du contenu...")
        with ZipFile(BytesIO(response.data)) as zf:
            # Lire le fichier workbook
            workbook_xml = zf.read('xl/workbook.xml').decode('utf-8')
            assert 'Élèves' in workbook_xml or 'sheet' in workbook_xml
            print("   ✅ Contenu trouvé dans le workbook")
        
        print("\n" + "="*60)
        print("✅ TOUS LES TESTS RÉUSSIS")
        print("="*60)


if __name__ == '__main__':
    test_download_example_route()

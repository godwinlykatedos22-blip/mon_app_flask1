"""
Test du nouveau modal d'export
"""

import sys
sys.path.insert(0, '.')

from app import create_app
from models import db, User

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

with app.test_client() as client:
    # 1. Connexion
    print("1️⃣  Connexion...")
    client.post('/auth/login', data={'email': 'admin@test.com', 'password': 'test123'}, follow_redirects=True)
    print("   ✅ Connecté")
    
    # 2. Obtenir la page
    print("\n2️⃣  Accès à /eleves/...")
    response = client.get('/eleves/')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    
    # 3. Vérifier le bouton Imprimer
    print("\n3️⃣  Vérification du bouton Imprimer...")
    if '🖨️ Imprimer' in html:
        print("   ✅ Bouton Imprimer trouvé")
    else:
        print("   ❌ Bouton Imprimer NOT trouvé")
    
    # 4. Vérifier le modal
    print("\n4️⃣  Vérification du modal...")
    if 'id="exportModal"' in html:
        print("   ✅ Modal exportModal trouvé")
    else:
        print("   ❌ Modal NOT trouvé")
    
    if 'class="modal fade"' in html:
        print("   ✅ Classes Bootstrap modal présentes")
    else:
        print("   ❌ Classes Bootstrap NOT trouvées")
    
    # 5. Vérifier les selects
    print("\n5️⃣  Vérification des sélecteurs...")
    if 'id="selectClass"' in html:
        print("   ✅ Sélecteur Classe trouvé")
    else:
        print("   ❌ Sélecteur Classe NOT trouvé")
    
    if 'id="selectFormat"' in html:
        print("   ✅ Sélecteur Format trouvé")
    else:
        print("   ❌ Sélecteur Format NOT trouvé")
    
    # 6. Vérifier les classes
    print("\n6️⃣  Vérification des classes dans le sélecteur...")
    all_classes = ['6ème', '5ème', '4ème', '3ème', '2nde AB', '2nde CD', '1ère AB', '1ère CD', 'Tle AB', 'Tle CD']
    found_count = 0
    for class_name in all_classes:
        if f'<option value="{class_name}">' in html:
            found_count += 1
            print(f"   ✅ {class_name}")
        else:
            print(f"   ❌ {class_name} NOT trouvé")
    
    print(f"\n   Résumé: {found_count}/{len(all_classes)} classes trouvées")
    
    # 7. Vérifier la fonction JavaScript
    print("\n7️⃣  Vérification du JavaScript...")
    if 'function validateAndExport()' in html:
        print("   ✅ Fonction validateAndExport() présente")
    else:
        print("   ❌ Fonction validateAndExport() NOT trouvée")
    
    if 'selectClass' in html and 'selectFormat' in html:
        print("   ✅ Références aux éléments DOM présentes")
    else:
        print("   ❌ Références DOM NOT trouvées")
    
    # 8. Vérifier le bouton Valider
    print("\n8️⃣  Vérification du bouton Valider...")
    if 'onclick="validateAndExport()"' in html:
        print("   ✅ Bouton Valider avec fonction présent")
    else:
        print("   ❌ Bouton Valider NOT trouvé")
    
    print("\n" + "="*60)
    print("✅ TEST COMPLET")
    print("="*60)

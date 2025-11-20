"""
Test de vérification de la page liste des élèves avec les nouvelles fonctionnalités
"""

import requests
from bs4 import BeautifulSoup

session = requests.Session()

# Connexion
print("1️⃣  Connexion à l'application...")
r = session.post('http://localhost:5000/auth/login', data={
    'email': 'admin@ecole.local',
    'password': 'admin123'
}, allow_redirects=True)
print(f"   Status: {r.status_code}")

# Accéder à la page de liste des élèves
print("\n2️⃣  Accès à la page de liste des élèves...")
r = session.get('http://localhost:5000/eleves/')
print(f"   Status: {r.status_code}")

if r.status_code == 200:
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Vérifier le bouton Imprimer
    print("\n3️⃣  Vérification du bouton Imprimer...")
    print_button = soup.find('button', string=lambda s: s and '🖨️ Imprimer' in s)
    if print_button:
        print("   ✅ Bouton Imprimer trouvé")
    else:
        print("   ❌ Bouton Imprimer NOT trouvé")
    
    # Vérifier les classes dans le menu
    print("\n4️⃣  Vérification des classes dans le menu...")
    all_classes = ['6ème', '5ème', '4ème', '3ème', '2nde AB', '2nde CD', '1ère AB', '1ère CD', 'Tle AB', 'Tle CD']
    for class_name in all_classes:
        if class_name in r.text:
            print(f"   ✅ {class_name}")
        else:
            print(f"   ❌ {class_name} NOT found")
    
    # Vérifier les tooltips
    print("\n5️⃣  Vérification des tooltips...")
    tooltips = soup.find_all('a', {'data-bs-toggle': 'tooltip'})
    print(f"   ✅ {len(tooltips)} tooltips trouvées")
    
    # Vérifier la fonction JS exportClass
    print("\n6️⃣  Vérification du code JavaScript...")
    if 'exportClass' in r.text:
        print("   ✅ Fonction exportClass présente")
    else:
        print("   ❌ Fonction exportClass NOT trouvée")
    
    if 'get-class-id' in r.text:
        print("   ✅ Route get-class-id référencée")
    else:
        print("   ❌ Route get-class-id NOT trouvée")
    
    # Test de la route get-class-id
    print("\n7️⃣  Test de la route /eleves/get-class-id/...")
    test_classes = ['6ème', '5ème', '4ème']
    for test_class in test_classes:
        r_api = session.get(f'http://localhost:5000/eleves/get-class-id/{test_class}')
        if r_api.status_code == 200:
            data = r_api.json()
            if 'class_id' in data:
                print(f"   ✅ {test_class}: {data.get('class_id', 'None')}")
            else:
                print(f"   ⚠️  {test_class}: pas de class_id")
        else:
            print(f"   ⚠️  {test_class}: {r_api.status_code}")

    print("\n" + "="*60)
    print("✅ VÉRIFICATION COMPLÈTE")
    print("="*60)
else:
    print(f"   ❌ Erreur {r.status_code}")

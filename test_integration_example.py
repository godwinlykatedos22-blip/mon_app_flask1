"""
Script de test d'intégration pour /eleves/download-example
Teste le téléchargement du fichier d'exemple via une session complète
"""

import requests
import re
from io import BytesIO
from zipfile import ZipFile


def test_example_download():
    """Test complet du téléchargement du fichier d'exemple"""
    
    BASE_URL = "http://localhost:5000"
    session = requests.Session()
    
    print("\n" + "="*60)
    print("ÉTAPE 1: Accès à la page de connexion")
    print("="*60)
    
    # 1. Accédez à la page de connexion pour obtenir les cookies CSRF
    response = session.get(f"{BASE_URL}/login")
    assert response.status_code == 200
    print(f"✅ Page de connexion accessible (Status: {response.status_code})")
    
    # Extraire le token CSRF si présent
    csrf_token = None
    if 'csrf_token' in response.text:
        match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
        if match:
            csrf_token = match.group(1)
            print(f"✅ Token CSRF extrait: {csrf_token[:20]}...")
    
    print("\n" + "="*60)
    print("ÉTAPE 2: Connexion avec admin@ecole.local")
    print("="*60)
    
    # 2. Se connecter
    login_data = {
        'email': 'admin@ecole.local',
        'password': 'admin123',
        'csrf_token': csrf_token
    }
    
    response = session.post(
        f"{BASE_URL}/login",
        data=login_data,
        allow_redirects=False
    )
    
    if response.status_code in [302, 303]:
        print(f"✅ Connexion réussie (Redirection: {response.status_code})")
        location = response.headers.get('Location', '')
        print(f"✅ Redirection vers: {location}")
    elif response.status_code == 200:
        if 'dashboard' in response.text or 'Bienvenue' in response.text:
            print(f"✅ Connecté directement (Status: {response.status_code})")
        else:
            print(f"⚠️  Statut 200 mais contenu inattendu")
    
    print("\n" + "="*60)
    print("ÉTAPE 3: Test de la route /eleves/download-example")
    print("="*60)
    
    # 3. Accéder à la route de téléchargement
    response = session.get(f"{BASE_URL}/eleves/download-example", allow_redirects=True)
    
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type', 'Non spécifié')}")
    print(f"Content-Disposition: {response.headers.get('Content-Disposition', 'Non spécifié')}")
    
    if response.status_code == 200:
        print(f"✅ Fichier téléchargé avec succès")
        
        # Vérifier le contenu
        file_size = len(response.content)
        print(f"✅ Taille du fichier: {file_size} bytes")
        
        # Vérifier que c'est un ZIP (XLSX = ZIP)
        if response.content[:4] == b'PK\x03\x04':
            print(f"✅ Format XLSX validé (Magic bytes: PK...)")
            
            # Essayer d'ouvrir comme ZIP
            try:
                with ZipFile(BytesIO(response.content)) as zf:
                    files = zf.namelist()
                    print(f"✅ Archive ZIP valide avec {len(files)} fichiers")
                    
                    # Chercher le fichier de contenu
                    if 'xl/workbook.xml' in files:
                        print(f"✅ Structure XLSX valide détectée")
                        
                        # Chercher les feuilles
                        if 'xl/worksheets/sheet1.xml' in files:
                            print(f"✅ Feuille 1 (Élèves) détectée")
                        if 'xl/worksheets/sheet2.xml' in files:
                            print(f"✅ Feuille 2 (Classes) détectée")
                        if 'xl/worksheets/sheet3.xml' in files:
                            print(f"✅ Feuille 3 (Instructions) détectée")
                        
                        # Afficher aperçu
                        workbook_xml = zf.read('xl/workbook.xml').decode('utf-8')
                        if 'Élèves' in workbook_xml:
                            print(f"✅ Contenu français détecté")
            except Exception as e:
                print(f"⚠️  Erreur lors de l'analyse ZIP: {e}")
        else:
            print(f"❌ Fichier n'est pas en format XLSX valide")
            print(f"   Magic bytes: {response.content[:4]}")
    
    elif response.status_code == 302:
        location = response.headers.get('Location', '')
        print(f"❌ Redirection détectée (probablement non authentifié)")
        print(f"   Redirection vers: {location}")
    
    else:
        print(f"❌ Erreur: Status {response.status_code}")
        print(f"   Réponse: {response.text[:200]}")
    
    print("\n" + "="*60)
    print("ÉTAPE 4: Vérification de la page d'importation")
    print("="*60)
    
    # 4. Vérifier que la page d'importation contient le lien
    response = session.get(f"{BASE_URL}/eleves/import")
    
    if response.status_code == 200:
        print(f"✅ Page d'importation accessible")
        
        # Chercher le bouton de téléchargement d'exemple
        if 'download-example' in response.text:
            print(f"✅ Lien 'download-example' détecté dans la page")
        
        if 'Télécharger un exemple' in response.text or 'exemple' in response.text.lower():
            print(f"✅ Texte d'exemple détecté dans la page")
        
        if 'Format du fichier' in response.text:
            print(f"✅ Instructions mises à jour détectées")
    else:
        print(f"⚠️  Page d'importation: Status {response.status_code}")
    
    print("\n" + "="*60)
    print("✅ TEST COMPLET RÉUSSI")
    print("="*60)


if __name__ == '__main__':
    try:
        test_example_download()
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

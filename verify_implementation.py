import requests

session = requests.Session()

# Connexion
r = session.post('http://localhost:5000/auth/login', data={
    'email': 'admin@ecole.local',
    'password': 'admin123'
})

print("1️⃣  Vérification de la page d'importation")
print("="*60)

# Page d'importation
r = session.get('http://localhost:5000/eleves/import')
print(f'Status: {r.status_code}')

# Vérifier la présence des boutons
if 'download-example' in r.text:
    print('✅ Lien download-example présent')
else:
    print('❌ Lien download-example absent')

if 'Télécharger un exemple' in r.text:
    print('✅ Texte "Télécharger un exemple" présent')
else:
    print('❌ Texte "Télécharger un exemple" absent')

if 'Format du fichier' in r.text:
    print('✅ Instructions mises à jour détectées')
else:
    print('❌ Instructions non détectées')

print("\n2️⃣  Test du téléchargement du fichier d'exemple")
print("="*60)

# Test du lien
r = session.get('http://localhost:5000/eleves/download-example')
print(f'Status: {r.status_code}')
print(f'Content-Type: {r.headers.get("Content-Type", "?")}')
print(f'Content-Length: {len(r.content)} bytes')

if r.status_code == 200 and r.content[:4] == b'PK\x03\x04':
    print('✅ Fichier XLSX téléchargé avec succès')
    print("\n3️⃣  Vérification de la structure du fichier")
    print("="*60)
    from zipfile import ZipFile
    from io import BytesIO
    with ZipFile(BytesIO(r.content)) as zf:
        sheets = [f for f in zf.namelist() if 'sheet' in f]
        print(f'✅ {len(sheets)} feuilles détectées')
else:
    print(f'❌ Erreur: {r.status_code}')

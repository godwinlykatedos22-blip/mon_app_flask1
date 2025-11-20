import requests
from io import BytesIO
from zipfile import ZipFile

session = requests.Session()

# 1. Connexion
print('1️⃣  Connexion...')
r = session.post('http://localhost:5000/auth/login', data={
    'email': 'admin@ecole.local',
    'password': 'admin123'
}, allow_redirects=True)
print(f'   Status: {r.status_code}')

# 2. Télécharger le fichier d'exemple
print('2️⃣  Téléchargement du fichier...')
r = session.get('http://localhost:5000/eleves/download-example')
print(f'   Status: {r.status_code}')
print(f'   Size: {len(r.content)} bytes')
print(f'   Content-Type: {r.headers.get("Content-Type", "?")}')

# 3. Valider le format
if r.status_code == 200:
    if r.content[:4] == b'PK\x03\x04':
        print('   ✅ Format XLSX valide (magic bytes)')
        try:
            with ZipFile(BytesIO(r.content)) as zf:
                sheets = [f for f in zf.namelist() if 'sheet' in f]
                print(f'   ✅ {len(sheets)} feuilles trouvées')
        except Exception as e:
            print(f'   ❌ Erreur ZIP: {e}')
    else:
        print(f'   ❌ Format invalide: {r.content[:10]}')
else:
    print(f'   ❌ Erreur {r.status_code}')
    if r.status_code == 302:
        print(f'      Redirection vers: {r.headers.get("Location", "?")}')

print('\n✅ Test terminé')

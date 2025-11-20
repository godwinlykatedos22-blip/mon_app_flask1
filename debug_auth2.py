import requests

session = requests.Session()

# Obtenir la page de login pour extraire le CSRF token
r = session.get('http://localhost:5000/auth/login')
print(f"Login page: {r.status_code}")

# Extraire le CSRF token
import re
match = re.search(r'name="csrf_token" value="([^"]+)"', r.text)
if match:
    csrf_token = match.group(1)
    print(f"✅ CSRF token trouvé: {csrf_token[:20]}...")
else:
    print("❌ CSRF token pas trouvé")
    csrf_token = None

# Essayer la connexion avec CSRF token
r = session.post('http://localhost:5000/auth/login', data={
    'email': 'admin@ecole.local',
    'password': 'admin123',
    'csrf_token': csrf_token
}, allow_redirects=False)

print(f"\nLogin response: {r.status_code}")
print(f"Location: {r.headers.get('Location', 'N/A')}")

# Vérifier les cookies
print(f"Cookies: {len(session.cookies)} cookies")
for k, v in session.cookies.items():
    print(f"  {k}: {v[:50]}...")

# Essayer d'accéder à /eleves/
r = session.get('http://localhost:5000/eleves/', allow_redirects=True)
print(f"\nEleves: {r.status_code}")
print(f"URL: {r.url}")

if 'Please log in' in r.text or 'Connexion' in r.text:
    print("❌ Toujours pas connecté")
elif 'Importer' in r.text or 'élèves' in r.text:
    print("✅ Connecté!")
else:
    print("❓ État indéterminé")

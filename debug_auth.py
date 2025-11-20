import requests
import json

session = requests.Session()

# Essayer la connexion
r = session.post('http://localhost:5000/auth/login', data={
    'email': 'admin@ecole.local',
    'password': 'admin123'
}, allow_redirects=False)

print(f"Login response: {r.status_code}")
print(f"Location header: {r.headers.get('Location', 'N/A')}")
print(f"Cookies: {dict(session.cookies)}")

# Vérifier si on a un cookie de session
if session.cookies:
    print("✅ Cookies présents")
else:
    print("❌ Pas de cookies")

# Essayer d'accéder à la page d'import avec redirection
r = session.get('http://localhost:5000/eleves/import', allow_redirects=True)
print(f"\nImport page: {r.status_code}")
print(f"Final URL: {r.url}")

# Vérifier le contenu
if 'Please log in' in r.text:
    print("❌ Toujours sur la page de login")
elif 'Importer' in r.text:
    print("✅ Sur la page d'import")
else:
    print("❓ Contenu inattendu")

# Afficher les 500 premiers chars
print("\nContenu:")
print(r.text[:500])

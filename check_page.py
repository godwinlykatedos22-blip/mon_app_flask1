import requests

session = requests.Session()
r = session.post('http://localhost:5000/auth/login', data={'email': 'admin@ecole.local', 'password': 'admin123'}, allow_redirects=True)
print(f"Login: {r.status_code}")

r = session.get('http://localhost:5000/eleves/import')
print(f"Import page: {r.status_code}")

if 'download-example' in r.text:
    print("✅ download-example trouvé")
else:
    print("❌ download-example NOT found")
    
if 'Télécharger un exemple' in r.text:
    print("✅ 'Télécharger un exemple' trouvé")
else:
    print("❌ 'Télécharger un exemple' NOT found")

if 'Format du fichier' in r.text:
    print("✅ 'Format du fichier' trouvé")
else:
    print("❌ 'Format du fichier' NOT found")

# Afficher aperçu
print("\nAperçu du contenu (premières 1500 chars):")
print(r.text[:1500])

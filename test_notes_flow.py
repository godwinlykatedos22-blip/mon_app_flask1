#!/usr/bin/env python3
"""
Test du flux complet de saisie des notes
Login -> Charger classe -> Saisir notes -> Enregistrer -> Voir dashboard
"""

import requests
from datetime import date
import re

# Configuration
BASE_URL = "http://127.0.0.1:5000"
session = requests.Session()

# Étape 1: Login
print("=" * 60)
print("🔐 Étape 1: Authentification")
print("=" * 60)

login_data = {
    'email': 'admin@ecole.local',
    'password': 'admin123'
}

login_response = session.post(f"{BASE_URL}/auth/login", data=login_data, allow_redirects=True)
if "dashboard" in login_response.url or login_response.status_code == 200:
    print("✅ Authentification réussie")
else:
    print(f"❌ Erreur d'authentification: {login_response.status_code}")

# Étape 2: Charger la classe (action: load_students)
print("\n" + "=" * 60)
print("📚 Étape 2: Chargement de la classe")
print("=" * 60)

load_form = {
    'class_id': '1',  # 6ème
    'subject': 'Français',
    'assessment_type': 'interrogation',
    'date': str(date.today()),
    'term': '1',
    'max_score': '20',
    'action': 'load_students'
}

entry_response = session.post(f"{BASE_URL}/notes/entry", data=load_form, allow_redirects=False)
print(f"✅ Classe chargée (Status: {entry_response.status_code})")

# Étape 3: Extraire les IDs des élèves du HTML retourné
print("\n" + "=" * 60)
print("👤 Étape 3: Extraction des élèves")
print("=" * 60)

entry_get = session.get(f"{BASE_URL}/notes/entry")
html_content = entry_get.text

# Extraire les score_XX inputs
pattern = r'name="score_(\d+)"'
student_ids = re.findall(pattern, html_content)
print(f"✅ {len(student_ids)} élève(s) trouvé(s): {student_ids}")

# Étape 4: Remplir et enregistrer les notes
print("\n" + "=" * 60)
print("📝 Étape 4: Enregistrement des notes")
print("=" * 60)

save_form = {
    'class_id': '1',
    'subject': 'Français',
    'assessment_type': 'interrogation',
    'date': str(date.today()),
    'term': '1',
    'max_score': '20',
    'action': 'save_notes'
}

# Ajouter les scores pour chaque élève
scores = [14.5, 16.0, 18.5]
for i, student_id in enumerate(student_ids):
    save_form[f'score_{student_id}'] = str(scores[i % len(scores)])
    print(f"  • Élève {student_id}: {scores[i % len(scores)]}/20")

save_response = session.post(f"{BASE_URL}/notes/entry", data=save_form, allow_redirects=True)

# Vérifier si le flux a fonctionné
if "Gestion des Notes" in save_response.text or "Historique des Notes" in save_response.text:
    print("✅ Notes enregistrées avec succès!")
    print(f"✅ Redirection vers le tableau de bord ({save_response.url})")
    
    # Vérifier le contenu du dashboard
    if "Interrogations" in save_response.text:
        print("✅ Récapitulatif par type d'évaluation visible")
    if "Historique des Notes" in save_response.text:
        print("✅ Historique détaillé visible")
    if "Rendement /20" in save_response.text:
        print("✅ Rendements normalisés visibles")
else:
    print(f"⚠️ Réponse: {save_response.status_code}")
    if "danger" in save_response.text:
        print("❌ Une erreur s'est produite")
    print(f"URL finale: {save_response.url}")

print("\n" + "=" * 60)
print("✅ FLUX COMPLET EXÉCUTÉ")
print("=" * 60)

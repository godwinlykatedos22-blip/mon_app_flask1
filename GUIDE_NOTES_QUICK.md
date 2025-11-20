# 🚀 GUIDE RAPIDE - MODULE NOTES

## 📍 Accès Principal
- URL: `http://localhost:5000/notes/`
- Nécessite: Login enseignant

---

## 📝 SAISIE QUOTIDIENNE (Recommandé)

### **Accès**
- Bouton: "➕ Saisie Quotidienne" sur page `/notes/`
- URL: `/notes/daily`

### **Étapes**
1. **Sélectionner les paramètres :**
   - 🎓 **Classe** : Choisir parmi liste
   - 📚 **Matière** : Saisir (ex: Français, Mathématiques)
   - 🎯 **Type** : ❓ Interrogation / 📝 Devoir / 📋 Composition
   - 📅 **Date** : Par défaut aujourd'hui
   - 🔢 **Trimestre** : 1, 2 ou 3
   - 🔢 **Note Maximale** : Par défaut 20.0

2. **Cliquer : "Saisir les notes"**
   - → Tableau avec tous les élèves de la classe s'affiche

3. **Remplir les notes**
   - Entrer note obtenue dans chaque champ
   - Notes entre 0 et la note maximale

4. **Enregistrer**
   - Cliquer : "✅ Enregistrer X note(s)"
   - → Notes sauvegardées + Messages parent générés automatiquement

---

## ➕ AJOUTER UNE NOTE INDIVIDUELLE

### **Accès**
- URL: `/notes/add`
- Bouton: "➕ Ajouter Note (Individuelle)"

### **Étapes**
1. Sélectionner **Élève**
2. Saisir **Matière**
3. Choisir **Type** de note
4. Entrer **Score** obtenu
5. Définir **Note maximale**
6. Sélectionner **Date** et **Trimestre**
7. Cliquer "Ajouter la note"
8. ✅ Message parent envoyé automatiquement

---

## 📊 CONSULTER LES NOTES

### **Page Principale** (`/notes/`)
- **Tableau complet** de toutes les notes
- **Filtres disponibles** :
  - 🏫 Classe
  - 📅 Trimestre
  - 🗓️ Date

- **Actions** :
  - ✏️ Modifier
  - 🗑️ Supprimer

---

## 📋 BULLETIN TRIMESTRIEL

### **Accès**
- **Via page élève** (détails élève)
- URL direct: `/notes/bulletin/<student_id>/<term>`

### **Contenu**
- 📝 Récapitulatif par matière
  - Moyenne Interrogations
  - Moyenne Devoirs
  - Moyenne Compositions
  - **Moyenne Générale**

- 📊 Tableau détaillé
  - Chaque note saisie
  - Date, Type, Score normalisé

---

## 📈 STATISTIQUES CLASSE

### **Accès**
- URL: `/notes/stats/<class_id>/<term>`
- Depuis page notes avec filtres

### **Données**
- 📊 Moyenne classe générale
- 📚 Par matière : Moyenne, Min, Max, Nombre de notes
- 🎨 Graphiques de progression
- 📊 Pourcentages visuels

---

## 💬 CORRESPONDANCE PARENT

### **Automatisée Après Saisie**
1. **Saisie note** → Système déclenche automatiquement
2. **MessageLog créé** avec statut `queued`
3. **Email/SMS/WhatsApp** envoyé aux parents (si configuré)
4. **Statut** mis à jour : `sent_email`, `sent_whatsapp`, etc.

### **Format Message**
```
📋 NOTES DU JOUR - 17/11/2025

Matière: Français

👤 Jean Dupont
   ❓ Interrogation
      Note: 17.5/20 (17.50/20)

👤 Sophie Dupont
   ❓ Interrogation
      Note: 14.0/20 (14.00/20)
```

### **Configuration Email** (Optionnel)
Ajouter au fichier `.env` ou variables système:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=noreply@ecole.local
SENDER_PASSWORD=motdepasse
```

---

## 🔄 WORKFLOW RECOMMANDÉ

### **Matin** : Préparer les classes
1. Ouvrir `/notes/daily`
2. Sélectionner classe et date
3. Rester sur page (ne pas valider)

### **Pendant le cours** : Saisie
1. Remplir les notes en temps réel
2. Valider à la fin du cours

### **Après cours** : Notifications
1. ✅ Messages envoyés automatiquement aux parents
2. Historique sauvegardé

### **Fin de trimestre** : Bulletins
1. Générer bulletins élèves
2. Consulter statistiques classe
3. Analyser performance globale

---

## ⚙️ PARAMÈTRES NOTES

| Élément | Valeur | Notes |
|---------|--------|-------|
| Note max défaut | 20.0 | Modifiable par matière |
| Trimestres | 1, 2, 3 | Année scolaire |
| Types notes | 3 types | Interrogation, Devoir, Composition |
| Normalisation | /20 | Automatique |

---

## 🎯 RACCOURCIS CLAVIER (Optionnel)

- `Tab` : Passer au champ suivant
- `Enter` : Valider formulaire (page saisie)
- `Ctrl+Shift+N` : Nouvelle note (navigateur)

---

## ❓ FAQ

**Q: Puis-je modifier une note après?**
A: Oui, cliquer ✏️ sur la note dans le tableau

**Q: Les parents reçoivent les messages?**
A: Oui si Email/SMS/WhatsApp configurés, sinon log de simulation

**Q: Que se passe-t-il en cas de doublon?**
A: Le système refuse (même élève, même jour, matière, type)

**Q: Comment générer un bulletin?**
A: `/notes/bulletin/<student_id>/<term>`

**Q: Puis-je exporter les notes?**
A: Via `/notes/`, télécharger tableau (export en développement)

---

## 🆘 DÉPANNAGE

| Problème | Solution |
|----------|----------|
| "Élève introuvable" | Vérifier inscription élève |
| "Classe vide" | Ajouter élèves à la classe |
| Messages non reçus | Configurer SMTP/API WhatsApp |
| Erreur doublon | Vérifier date/matière/type |

---

**Besoin d'aide?** Contacter: support@ecole.local

# Guide d'intégration Twilio pour l'envoi WhatsApp

## Objectif
Configurer l'envoi réel de messages WhatsApp via Twilio (WhatsApp Business API via Twilio)

## Variables d'environnement requises
- `TWILIO_ACCOUNT_SID` : SID du compte Twilio
- `TWILIO_AUTH_TOKEN` : Token d'authentification Twilio
- `TWILIO_WHATSAPP_FROM` : Adresse expéditeur WhatsApp Twilio, ex: `whatsapp:+1415XXXXXXX`

(Optionnel)
- `TWILIO_ENABLED` : `1` ou `true` pour forcer l'utilisation de Twilio

## Étapes pour obtenir les identifiants Twilio
1. Créer un compte Twilio (https://www.twilio.com/)
2. Accéder à la console (Dashboard) → Copier `Account SID` et `Auth Token`
3. Sous Messaging → Try it out → WhatsApp → suivre la procédure pour obtenir un numéro WhatsApp (ou sandbox)
4. Copier l'identifiant `whatsapp:+...` fourni

## Configuration locale (PowerShell)
```powershell
$env:TWILIO_ACCOUNT_SID = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
$env:TWILIO_AUTH_TOKEN = "your_auth_token"
$env:TWILIO_WHATSAPP_FROM = "whatsapp:+1415XXXXXXX"
```

Pour PowerShell permanent, ajouter au profil ou utiliser un fichier `.env` et `python-dotenv`.

## Exemple d'utilisation (code)
Le service `ParentMessagingService._send_whatsapp(parent, content)` utilise Twilio automatiquement
si les variables d'environnement sont définies et si le paquet `twilio` est installé.

Extrait d'envoi:
```python
from twilio.rest import Client
client = Client(account_sid, auth_token)
message = client.messages.create(
    from_='whatsapp:+1415XXXXXXX',
    to=f'whatsapp:{parent.phone_e164}',
    body=message_content
)
print(message.sid)
```

## Tester l'envoi
1. Mettre les variables d'environnement
2. Installer la dépendance:
```powershell
\.venv\Scripts\pip install -r requirements.txt
```
3. Lancer le script de test (optionnel):
```powershell
\.venv\Scripts\python.exe test_whatsapp_correspondence.py
```

> Si Twilio est configuré, l'envoi passera par Twilio.
> Sinon, le système utilisera `pywhatkit` si installé, ou logera en mode stub.

## Retry & traçabilité

- Les envois via Twilio sont tentés jusqu'à 3 fois (réglable dans `BulkMessageProcessor`).
- Chaque tentative incrémente `MessageLog.attempts` et stocke `MessageLog.last_error` si échec.
- Le `MessageLog.twilio_sid` est enregistré quand Twilio retourne un SID pour permettre un suivi précis.
- Utiliser `BulkMessageProcessor.process_pending_messages()` en tâche cron pour retraitement automatique des échecs.

Exemple: relancer les messages en erreur toutes les 10 minutes via cron ou un scheduler:

```powershell
# Exemple Windows Task Scheduler ou service qui exécute:
\.\venv\Scripts\python.exe -c "from services.messaging import BulkMessageProcessor; BulkMessageProcessor.process_pending_messages()"
```

## Gestion des erreurs & bonnes pratiques
- Surveiller `MessageLog` pour l'état des envois.
- Mettre en place une politique de retry (ex: 3 tentatives) pour erreurs transitoires.
- Respecter les règles d'opt-in: vérifier `parent.whatsapp_optin` avant envoi.
- Pour production, préférez un numéro officiel (non sandbox) et vérifiez les quotas/coûts.

## Notes légales
- Vérifier conformité RGPD et consentement explicite des parents.
- Conserver une trace des messages envoyés (déjà fait via `MessageLog`).

## Support
Pour aide: ajouter une issue dans le repo ou contacter l'équipe d'intégration.

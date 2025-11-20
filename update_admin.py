from app import create_app
from models import db, User

app = create_app()
with app.app_context():
    user = User.query.filter_by(email='godwindossa22@gmail.com').first()
    if user:
        print(f"Utilisateur trouvé: {user.email}")
        print(f"Rôle avant: {user.role}")
        user.role = 'admin'
        db.session.commit()
        print(f"Rôle après: {user.role}")
        print("✅ Mise à jour terminée")
    else:
        print("❌ Utilisateur non trouvé")

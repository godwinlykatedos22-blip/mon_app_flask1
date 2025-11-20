"""
Script de test pour démontrer le système de rôles et les accès restreints
"""

from app import create_app
from models import db, User, Professor

app = create_app()

with app.app_context():
    # Nettoyer les comptes test existants
    User.query.filter(User.email.in_(['admin@test.local', 'professor@test.local', 'director@test.local'])).delete()
    Professor.query.all()
    db.session.commit()

    # Créer des comptes de test avec différents rôles
    print("📝 Création des comptes de test...")

    # Admin
    admin = User(email='admin@test.local', name='Admin Test', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)
    print("✅ Admin créé : admin@test.local / admin123")

    # Director
    director = User(email='director@test.local', name='Directeur Test', role='director')
    director.set_password('director123')
    db.session.add(director)
    print("✅ Directeur créé : director@test.local / director123")

    # Teacher
    teacher = User(email='teacher@test.local', name='Professeur Test', role='teacher')
    teacher.set_password('teacher123')
    db.session.add(teacher)
    print("✅ Professeur créé : teacher@test.local / teacher123")

    db.session.commit()

    # Créer des professeurs
    print("\n📚 Création de professeurs...")
    
    prof1 = Professor(
        first_name='Jean',
        last_name='Dupont',
        email='jean.dupont@ecole.fr',
        phone='+33612345678',
        subjects='Mathématiques, Informatique'
    )
    db.session.add(prof1)

    prof2 = Professor(
        first_name='Marie',
        last_name='Martin',
        email='marie.martin@ecole.fr',
        phone='+33687654321',
        subjects='Français, Littérature'
    )
    db.session.add(prof2)

    db.session.commit()
    print("✅ Professeurs créés")

    # Test des permissions
    print("\n🔐 Test des permissions:")
    print(f"  Admin est admin ? {admin.is_admin()}")
    print(f"  Admin est directeur ? {admin.is_director()}")
    print(f"  Admin est professeur ? {admin.is_teacher()}")
    print()
    print(f"  Directeur est admin ? {director.is_admin()}")
    print(f"  Directeur est directeur ? {director.is_director()}")
    print(f"  Directeur est professeur ? {director.is_teacher()}")
    print()
    print(f"  Professeur est admin ? {teacher.is_admin()}")
    print(f"  Professeur est directeur ? {teacher.is_director()}")
    print(f"  Professeur est professeur ? {teacher.is_teacher()}")

    print("\n✨ Données de test créées avec succès!")
    print("\nVous pouvez maintenant tester les différents rôles:")
    print("  • Admin: admin@test.local / admin123 → Accès à TOUT")
    print("  • Directeur: director@test.local / director123 → Gestion données")
    print("  • Professeur: teacher@test.local / teacher123 → Saisie notes")

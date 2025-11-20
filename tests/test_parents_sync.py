import sys, os
sys.path.insert(0, os.path.abspath(os.getcwd()))

from app import create_app
from models import db, Classe, Student, Parent

class TestConfig:
    SECRET_KEY = "test"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    TESTING = True
    LOGIN_DISABLED = True


def run_test():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

        # Ajouter une classe
        classe = Classe(name="6ème A")
        db.session.add(classe)
        db.session.commit()

        client = app.test_client()

        print("=" * 60)
        print("TEST: Inscription élève avec parent + synchronisation")
        print("=" * 60)

        # 1. Inscrire un élève avec parent
        data = {
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'birthdate': '2008-05-01',
            'class_id': str(classe.id),
            'parent_first_name': 'Marie',
            'parent_last_name': 'Dupont',
            'parent_phone': '+33123456789',
            'parent_whatsapp': 'y',
            'submit': 'Enregistrer'
        }

        resp = client.post('/eleves/add', data=data, follow_redirects=False)
        print(f"\n1️⃣ Inscription élève : Status {resp.status_code}")
        assert resp.status_code == 302, "L'inscription devrait rediriger"

        # Vérifier l'élève
        student = Student.query.first()
        assert student is not None, "L'élève devrait être créé"
        print(f"   ✓ Élève créé : {student.full_name}")

        # Vérifier le parent
        parent = Parent.query.first()
        assert parent is not None, "Le parent devrait être créé"
        print(f"   ✓ Parent créé : {parent.first_name} {parent.last_name}")

        # Vérifier la relation
        assert student in parent.students, "L'élève devrait être lié au parent"
        assert parent in student.parents, "Le parent devrait être lié à l'élève"
        print(f"   ✓ Lien établi : parent ↔ élève")

        # 2. Accéder à la page des parents
        print(f"\n2️⃣ Accès page parents : Status", end=" ")
        resp = client.get('/parents/')
        print(resp.status_code)
        assert resp.status_code == 200, "Page parents devrait être accessible"

        # Vérifier que les données sont dans la réponse
        assert parent.first_name.encode() in resp.data, "Nom parent devrait être visible"
        assert parent.last_name.encode() in resp.data, "Prénom parent devrait être visible"
        assert student.full_name.encode() in resp.data, "Élève lié devrait être visible"
        print(f"   ✓ Page affiche : {parent.first_name} {parent.last_name}")
        print(f"   ✓ Page affiche élève lié : {student.full_name}")

        # 3. Inscrire un deuxième élève du même parent
        print(f"\n3️⃣ Inscription 2ème élève même parent")
        data2 = {
            'first_name': 'Sophie',
            'last_name': 'Dupont',
            'birthdate': '2010-03-15',
            'class_id': str(classe.id),
            'parent_first_name': 'Marie',
            'parent_last_name': 'Dupont',
            'parent_phone': '+33123456789',
            'parent_whatsapp': 'y',
            'submit': 'Enregistrer'
        }

        resp = client.post('/eleves/add', data=data2, follow_redirects=False)
        print(f"   Status {resp.status_code}")

        student2 = Student.query.filter_by(first_name='Sophie').first()
        assert student2 is not None, "Le 2ème élève devrait être créé"
        print(f"   ✓ 2ème élève créé : {student2.full_name}")

        # Vérifier que le parent a les 2 élèves
        parent = Parent.query.first()
        assert len(parent.students) == 2, "Le parent devrait avoir 2 élèves"
        print(f"   ✓ Parent a {len(parent.students)} élèves liés")

        # 4. Vérifier la page parents mise à jour
        print(f"\n4️⃣ Vérification page parents")
        resp = client.get('/parents/')
        assert student2.full_name.encode() in resp.data, "2ème élève devrait être visible"
        print(f"   ✓ Page affiche 2 élèves liés au parent")

        print("\n" + "=" * 60)
        print("✅ TOUS LES TESTS SONT PASSÉS !")
        print("=" * 60)
        print("\n📋 Résumé :")
        print(f"   - Parents en base : {Parent.query.count()}")
        print(f"   - Élèves en base : {Student.query.count()}")
        parent = Parent.query.first()
        print(f"   - Élèves du parent '{parent.first_name} {parent.last_name}' : {len(parent.students)}")


if __name__ == '__main__':
    run_test()

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

        # Ajouter des élèves
        for i in range(3):
            student = Student(
                first_name=f"Élève{i}",
                last_name=f"Test{i}",
                class_id=classe.id
            )
            db.session.add(student)
        db.session.commit()

        client = app.test_client()

        # Test 1: Voir les détails d'un élève
        print("=" * 50)
        print("TEST 1: Voir les détails d'un élève")
        print("=" * 50)
        resp = client.get('/eleves/details/1')
        print(f"Status: {resp.status_code}")
        assert resp.status_code == 200, "La page de détails devrait retourner 200"
        print("✓ Page de détails accessible")

        # Test 2: Exporter Excel
        print("\n" + "=" * 50)
        print("TEST 2: Exporter Excel par classe")
        print("=" * 50)
        resp = client.get(f'/eleves/export/excel/{classe.id}')
        print(f"Status: {resp.status_code}")
        assert resp.status_code == 200, "L'export Excel devrait retourner 200"
        assert resp.content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        print(f"✓ Export Excel généré ({len(resp.data)} bytes)")

        # Test 3: Exporter PDF
        print("\n" + "=" * 50)
        print("TEST 3: Exporter PDF par classe")
        print("=" * 50)
        resp = client.get(f'/eleves/export/pdf/{classe.id}')
        print(f"Status: {resp.status_code}")
        assert resp.status_code == 200, "L'export PDF devrait retourner 200"
        assert resp.content_type == "application/pdf"
        print(f"✓ Export PDF généré ({len(resp.data)} bytes)")

        # Test 4: Exporter Word
        print("\n" + "=" * 50)
        print("TEST 4: Exporter Word par classe")
        print("=" * 50)
        resp = client.get(f'/eleves/export/word/{classe.id}')
        print(f"Status: {resp.status_code}")
        assert resp.status_code == 200, "L'export Word devrait retourner 200"
        assert resp.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        print(f"✓ Export Word généré ({len(resp.data)} bytes)")

        print("\n" + "=" * 50)
        print("✅ TOUS LES TESTS SONT PASSÉS !")
        print("=" * 50)


if __name__ == '__main__':
    run_test()

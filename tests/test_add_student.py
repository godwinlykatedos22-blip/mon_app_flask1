# test_add_student.py

import sys, os
# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.getcwd()))

import pytest
from app import create_app
from models import db, Classe, Student, Parent

@pytest.fixture
def app():
    class TestConfig:
        SECRET_KEY = "test"
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        WTF_CSRF_ENABLED = False
        TESTING = True
        LOGIN_DISABLED = True

    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def setup_classe(app):
    with app.app_context():
        classe = Classe(name="6ème")
        db.session.add(classe)
        db.session.commit()
        return classe

def test_add_student(client, setup_classe):
    data = {
        'first_name': 'Jean',
        'last_name': 'Dupont',
        'birthdate': '2008-05-01',
        'class_id': str(setup_classe.id),
        'parent_first_name': 'Marie',
        'parent_last_name': 'Dupont',
        'parent_phone': '+33123456789',
        'parent_whatsapp': 'y',
        'submit': 'Enregistrer'
    }

    resp = client.post('/eleves/add', data=data, follow_redirects=False)
    assert resp.status_code == 200

    with client.application.app_context():
        students = Student.query.all()
        assert len(students) == 1
        assert students[0].first_name == 'Jean'
        assert students[0].last_name == 'Dupont'

        parents = Parent.query.all()
        assert len(parents) == 1
        assert parents[0].first_name == 'Marie'
        assert parents[0].last_name == 'Dupont'

def test_minimal():
    assert 1 + 1 == 2

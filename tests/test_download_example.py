"""
Test de la route /eleves/download-example
Vérifie que le fichier d'exemple peut être téléchargé avec succès
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest


@pytest.fixture
def app():
    from app import create_app
    from models import db
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.create_all()
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def create_admin(app):
    from models import User
    with app.app_context():
        admin = User(email='admin@test.com', name='Admin', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()


def test_download_example_file(client, create_admin):
    response = client.get('/eleves/download-example')
    assert response.status_code in [200, 302]
    if response.status_code == 302:
        assert '/login' in response.location
    else:
        assert response.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        assert len(response.data) > 0


def test_download_example_with_login(client, create_admin):
    client.post('/login', data={
        'email': 'admin@test.com',
        'password': 'admin123'
    }, follow_redirects=True)
    response = client.get('/eleves/download-example')
    assert response.status_code == 200
    assert response.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert len(response.data) > 1000
    assert response.data[:4] == b'PK\x03\x04'


def test_download_example_headers(client, create_admin):
    client.post('/login', data={
        'email': 'admin@test.com',
        'password': 'admin123'
    }, follow_redirects=True)
    response = client.get('/eleves/download-example')
    assert 'Content-Disposition' in response.headers
    assert 'exemple_import_eleves.xlsx' in response.headers['Content-Disposition']
    assert 'attachment' in response.headers['Content-Disposition']

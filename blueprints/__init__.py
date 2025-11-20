# blueprints/__init__.py

from flask import Flask

# Importation des blueprints
from .auth.routes import auth_bp
from .eleves.routes import eleves_bp
from .notes.routes import notes_bp
from .parents.routes import parents_bp
from .admin import admin_bp


def register_blueprints(app: Flask):
    """Enregistre tous les blueprints de l'application."""

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(eleves_bp, url_prefix="/eleves")
    app.register_blueprint(notes_bp, url_prefix="/notes")
    app.register_blueprint(parents_bp, url_prefix="/parents")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # Ajout des blueprints manquants
    from .professors.routes import professors_bp
    from .accounts.routes import accounts_bp
    app.register_blueprint(professors_bp, url_prefix="/professors")
    app.register_blueprint(accounts_bp, url_prefix="/accounts")

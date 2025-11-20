# app.py

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, redirect, url_for
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, login_required
from models import db, User, Student, Classe
from blueprints.admin import DEFAULT_YEAR
from models import SchoolYear


# -------------------------
# Configuration centralisée
# -------------------------
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change_this_secret_key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///app_gestion.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOG_FILE = os.environ.get("LOG_FILE", "app_gestion.log")
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")


# -------------------------
# Extensions
# -------------------------
login_manager = LoginManager()
login_manager.login_view = "auth.login"
migrate = Migrate()


# -------------------------
# Création de l'application
# -------------------------
def create_app(config_class=Config):
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(config_class)

    # Initialiser extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    setup_logging(app)

    # -------------------------
    # Routes principales
    # -------------------------
    @app.route("/")
    def home():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return redirect(url_for("auth.login"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        total_students = Student.query.count()
        classes = Classe.query.order_by(Classe.name).all()
        active_year = SchoolYear.query.filter_by(active=True).first()
        current_year = active_year.year if active_year else DEFAULT_YEAR
        return render_template(
            "dashboard.html",
            total_students=total_students,
            classes=classes,
            current_year=current_year
        )

    @app.route("/students")
    @login_required
    def students_list():
        students = Student.query.all()
        return render_template("students_list.html", students=students)

    # -------------------------
    # Commande CLI : initdb
    # -------------------------
    @app.cli.command("initdb")
    def initdb_command():
        with app.app_context():
            db.drop_all()
            db.create_all()

            if not User.query.filter_by(email="admin@ecole.local").first():
                admin = User(email="admin@ecole.local", name="Admin", role="admin")
                admin.set_password("admin123")
                db.session.add(admin)
                db.session.commit()
                print("Base initialisée — admin@ecole.local / admin123")
            else:
                print("L'utilisateur admin existe déjà.")

    # -------------------------
    # Enregistrer blueprints
    # -------------------------
    from blueprints import register_blueprints
    register_blueprints(app)

    # -------------------------
    # Initialiser les classes prédéfinies
    # -------------------------
    with app.app_context():
        db.create_all()
        
        # Classes prédéfinies
        predefined_classes = [
            '6ème', '5ème', '4ème', '3ème', 
            '2nde AB', '2nde CD', 
            '1ère AB', '1ère CD', 
            'Tle AB', 'Tle CD'
        ]
        
        for class_name in predefined_classes:
            if not Classe.query.filter_by(name=class_name).first():
                new_class = Classe(name=class_name)
                db.session.add(new_class)
        
        db.session.commit()

    return app


# -------------------------
# Logging
# -------------------------
def setup_logging(app):
    if app.debug or app.testing:
        return

    log_level = getattr(logging, app.config.get("LOG_LEVEL", "INFO").upper(), logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    handler = RotatingFileHandler(app.config["LOG_FILE"], maxBytes=10 * 1024 * 1024, backupCount=3)
    handler.setFormatter(formatter)
    handler.setLevel(log_level)

    app.logger.setLevel(log_level)
    app.logger.addHandler(handler)
    app.logger.info("Logging initialisé.")


# -------------------------
# Flask-Login
# -------------------------
@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None


# -------------------------
# Exécution directe
# -------------------------
if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)

# Pour Flask CLI / WSGI servers
# (ne pas créer une deuxième instance)

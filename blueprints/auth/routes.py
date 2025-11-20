# blueprints/auth/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from models import db, User
from forms import LoginForm, RegisterForm
from werkzeug.security import generate_password_hash

auth_bp = Blueprint("auth", __name__, template_folder="../../templates")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Vérifier si l'utilisateur existe déjà
        if User.query.filter_by(email=form.email.data).first():
            flash("Cet email est déjà utilisé.", "danger")
            return redirect(url_for("auth.register"))

        # Créer l'utilisateur
        user = User(
            email=form.email.data
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash("Compte créé avec succès 🎉 Vous pouvez vous connecter.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)



@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                flash("Connexion réussie ✅", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("Email ou mot de passe incorrect", "danger")
        else:
            # Afficher les erreurs de validation du formulaire
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Erreur {field}: {error}", "danger")
    return render_template("login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Déconnexion réussie 👋", "info")
    return redirect(url_for("auth.login"))



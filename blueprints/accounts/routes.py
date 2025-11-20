"""
Routes pour la gestion des comptes utilisateurs
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from models import db, User

accounts_bp = Blueprint('accounts', __name__, url_prefix='/accounts', template_folder='../../templates')


def admin_required(f):
    """Décorateur pour vérifier si l'utilisateur est admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Vous devez être connecté.", "danger")
            return redirect(url_for('auth.login'))
        if not current_user.is_admin():
            flash("Accès refusé. Administrateur requis.", "danger")
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@accounts_bp.route('/', methods=['GET'])
@login_required
@admin_required
def list_accounts():
    """Afficher la liste des comptes utilisateurs"""
    users = User.query.all()
    return render_template('accounts/accounts_list.html', users=users)


@accounts_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_account():
    """Ajouter un compte utilisateur"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        name = request.form.get('name', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'teacher')

        if not email or not name or not password:
            flash("Email, nom et mot de passe sont obligatoires.", "warning")
            return redirect(url_for('accounts.add_account'))

        # Vérifier si email existe déjà
        existing = User.query.filter_by(email=email).first()
        if existing:
            flash("Un compte avec cet email existe déjà.", "danger")
            return redirect(url_for('accounts.add_account'))

        user = User(email=email, name=name, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash(f"Compte {email} ({role}) créé avec succès.", "success")
        return redirect(url_for('accounts.list_accounts'))

    return render_template('accounts/accounts_form.html', user=None, roles=['admin', 'director', 'teacher'])


@accounts_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_account(id):
    """Modifier un compte utilisateur"""
    user = User.query.get_or_404(id)

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        name = request.form.get('name', '').strip()
        role = request.form.get('role', 'teacher')
        is_active = request.form.get('is_active') == 'on'
        password = request.form.get('password', '').strip()

        if not email or not name:
            flash("Email et nom sont obligatoires.", "warning")
            return redirect(url_for('accounts.edit_account', id=id))

        # Vérifier si email existe déjà (sauf pour l'utilisateur actuel)
        existing = User.query.filter_by(email=email).filter(User.id != id).first()
        if existing:
            flash("Un autre compte avec cet email existe.", "danger")
            return redirect(url_for('accounts.edit_account', id=id))

        user.email = email
        user.name = name
        user.role = role
        user.is_active = is_active

        if password:
            user.set_password(password)

        db.session.commit()
        flash(f"Compte {email} modifié avec succès.", "success")
        return redirect(url_for('accounts.list_accounts'))

    return render_template('accounts/accounts_form.html', user=user, roles=['admin', 'director', 'teacher'])


@accounts_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_account(id):
    """Supprimer un compte utilisateur"""
    # Empêcher de supprimer son propre compte
    if id == current_user.id:
        flash("Vous ne pouvez pas supprimer votre propre compte.", "danger")
        return redirect(url_for('accounts.list_accounts'))

    user = User.query.get_or_404(id)
    email = user.email
    db.session.delete(user)
    db.session.commit()
    flash(f"Compte {email} supprimé avec succès.", "success")
    return redirect(url_for('accounts.list_accounts'))


@accounts_bp.route('/<int:id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_account_status(id):
    """Activer/Désactiver un compte"""
    if id == current_user.id:
        flash("Vous ne pouvez pas désactiver votre propre compte.", "danger")
        return redirect(url_for('accounts.list_accounts'))

    user = User.query.get_or_404(id)
    user.is_active = not user.is_active
    db.session.commit()
    status = "activé" if user.is_active else "désactivé"
    flash(f"Compte {user.email} {status}.", "success")
    return redirect(url_for('accounts.list_accounts'))

"""
Routes pour la gestion des professeurs
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from models import db, Professor

professors_bp = Blueprint('professors', __name__, url_prefix='/professors', template_folder='../../templates')


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


@professors_bp.route('/', methods=['GET'])
@login_required
@admin_required
def list_professors():
    """Afficher la liste des professeurs"""
    professors = Professor.query.all()
    return render_template('professors/professors_list.html', professors=professors)


@professors_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_professor():
    """Ajouter un professeur"""
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        subjects = request.form.get('subjects', '').strip()

        if not first_name or not last_name or not email:
            flash("Nom, prénom et email sont obligatoires.", "warning")
            return redirect(url_for('professors.add_professor'))

        # Vérifier si email existe déjà
        existing = Professor.query.filter_by(email=email).first()
        if existing:
            flash("Un professeur avec cet email existe déjà.", "danger")
            return redirect(url_for('professors.add_professor'))

        professor = Professor(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            subjects=subjects
        )
        db.session.add(professor)
        db.session.commit()
        flash(f"Professeur {professor.full_name} ajouté avec succès.", "success")
        return redirect(url_for('professors.list_professors'))

    return render_template('professors/professors_form.html', professor=None)


@professors_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_professor(id):
    """Modifier un professeur"""
    professor = Professor.query.get_or_404(id)

    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        subjects = request.form.get('subjects', '').strip()
        is_active = request.form.get('is_active') == 'on'

        if not first_name or not last_name or not email:
            flash("Nom, prénom et email sont obligatoires.", "warning")
            return redirect(url_for('professors.edit_professor', id=id))

        # Vérifier si email existe déjà (sauf pour le professeur actuel)
        existing = Professor.query.filter_by(email=email).filter(Professor.id != id).first()
        if existing:
            flash("Un autre professeur avec cet email existe.", "danger")
            return redirect(url_for('professors.edit_professor', id=id))

        professor.first_name = first_name
        professor.last_name = last_name
        professor.email = email
        professor.phone = phone
        professor.subjects = subjects
        professor.is_active = is_active

        db.session.commit()
        flash(f"Professeur {professor.full_name} modifié avec succès.", "success")
        return redirect(url_for('professors.list_professors'))

    return render_template('professors/professors_form.html', professor=professor)


@professors_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_professor(id):
    """Supprimer un professeur"""
    professor = Professor.query.get_or_404(id)
    name = professor.full_name
    db.session.delete(professor)
    db.session.commit()
    flash(f"Professeur {name} supprimé avec succès.", "success")
    return redirect(url_for('professors.list_professors'))

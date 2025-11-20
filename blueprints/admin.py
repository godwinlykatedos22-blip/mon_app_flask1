from flask import Blueprint, request, redirect, url_for, flash, session
from flask_login import login_required
from models import db, SchoolYear

admin_bp = Blueprint('admin', __name__)

DEFAULT_YEAR = '2025-2026'

@admin_bp.route('/set-school-year', methods=['POST'])
@login_required
def set_school_year():
    year = request.form.get('school_year')
    if year:
        # Désactiver toutes les années
        SchoolYear.query.update({SchoolYear.active: False})
        # Activer ou créer l'année sélectionnée
        school_year = SchoolYear.query.filter_by(year=year).first()
        if not school_year:
            school_year = SchoolYear(year=year, active=True)
            db.session.add(school_year)
        else:
            school_year.active = True
        db.session.commit()
        flash(f"Année scolaire changée pour : {year}", "success")
    else:
        flash("Aucune année sélectionnée.", "warning")
    return redirect(url_for('dashboard'))

@admin_bp.route('/close-and-open-year', methods=['POST'])
@login_required
def close_and_open_year():
    years = ["2023-2024", "2024-2025", "2025-2026", "2026-2027"]
    active_year = SchoolYear.query.filter_by(active=True).first()
    current_year = active_year.year if active_year else DEFAULT_YEAR
    try:
        idx = years.index(current_year)
        if idx + 1 < len(years):
            # Désactiver toutes les années
            SchoolYear.query.update({SchoolYear.active: False})
            # Activer ou créer la nouvelle année
            next_year = years[idx + 1]
            school_year = SchoolYear.query.filter_by(year=next_year).first()
            if not school_year:
                school_year = SchoolYear(year=next_year, active=True)
                db.session.add(school_year)
            else:
                school_year.active = True
            db.session.commit()
            flash(f"Nouvelle année scolaire ouverte : {next_year}", "success")
        else:
            flash("Aucune année suivante disponible.", "warning")
    except ValueError:
        flash("Année courante inconnue.", "danger")
    return redirect(url_for('dashboard'))

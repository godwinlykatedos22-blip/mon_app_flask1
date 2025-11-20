# blueprints/parents/routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from models import db, Parent
from forms import ParentForm

parents_bp = Blueprint("parents", __name__, url_prefix="/parents", template_folder="../../templates")

# --------------------------------------------------------
# LISTE DES PARENTS
# --------------------------------------------------------
@parents_bp.route("/")
@login_required
def list_parents():
    parents = Parent.query.all()
    return render_template("parents.html", parents=parents)


# --------------------------------------------------------
# AJOUT D’UN PARENT
# --------------------------------------------------------
@parents_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_parent():
    form = ParentForm()

    if form.validate_on_submit():
        parent = Parent(
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            phone_e164=form.phone_e164.data.strip() if form.phone_e164.data else None,
            whatsapp_optin=form.whatsapp_optin.data,
        )

        db.session.add(parent)
        db.session.commit()

        flash("Parent ajouté avec succès ✅", "success")
        return redirect(url_for("parents.list_parents"))

    return render_template("parents_form.html", form=form)


# --------------------------------------------------------
# MODIFICATION D’UN PARENT
# --------------------------------------------------------
@parents_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_parent(id):
    parent = Parent.query.get_or_404(id)
    form = ParentForm(obj=parent)

    if form.validate_on_submit():
        parent.first_name = form.first_name.data.strip()
        parent.last_name = form.last_name.data.strip()
        parent.phone_e164 = form.phone_e164.data.strip() if form.phone_e164.data else None
        parent.whatsapp_optin = form.whatsapp_optin.data

        db.session.commit()
        flash("Parent mis à jour ✏️", "success")
        return redirect(url_for("parents.list_parents"))

    return render_template("parents_form.html", form=form, edit=True)


# --------------------------------------------------------
# SUPPRESSION D’UN PARENT
# --------------------------------------------------------
@parents_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_parent(id):
    parent = Parent.query.get_or_404(id)

    db.session.delete(parent)
    db.session.commit()

    flash("Parent supprimé 🗑️", "info")
    return redirect(url_for("parents.list_parents"))

# Route pour envoyer un message WhatsApp
@parents_bp.route('/envoyer_message/<int:id>')
def envoyer_message(id):
    parent = Parent.query.get_or_404(id)
    # Logique pour envoyer le message (ex: via API WhatsApp)
    return f"Message envoyé au parent {parent.nom}"
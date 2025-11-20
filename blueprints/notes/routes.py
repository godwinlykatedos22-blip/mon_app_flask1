# blueprints/notes/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from models import db, Assessment, Student, Classe, Parent, MessageLog
from forms import AssessmentForm, BulkAssessmentForm
from services import ParentMessagingService
from datetime import datetime, date
from sqlalchemy import func

notes_bp = Blueprint("notes", __name__, template_folder="../../templates")


def admin_or_director_required(f):
    """Décorateur pour restreindre l'accès aux administrateurs et directeurs."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Vous devez être connecté.", "danger")
            return redirect(url_for('auth.login'))
        # Assumer que User a les méthodes is_admin/is_director
        if not (hasattr(current_user, 'is_admin') and current_user.is_admin()) and not (hasattr(current_user, 'is_director') and current_user.is_director()):
            flash("Accès refusé. Droits insuffisants.", "danger")
            return redirect(url_for('notes.notes_dashboard'))
        return f(*args, **kwargs)
    return decorated


# --------------------------------------------------------
# TABLEAU DE BORD NOTES (Dashboard avec synthèse)
# --------------------------------------------------------
@notes_bp.route("/dashboard")
@login_required
def notes_dashboard():
    """Tableau de bord de gestion des notes avec filtres et récapitulatif"""
    from sqlalchemy import and_
    
    # Paramètres de filtrage
    class_id = request.args.get("class_id", type=int)
    subject = request.args.get("subject", type=str)
    term = request.args.get("term", type=int)
    date_str = request.args.get("date", type=str)
    
    # Construire la requête avec filtres
    query = Assessment.query
    
    if class_id:
        query = query.join(Student).filter(Student.class_id == class_id)
    
    if subject:
        query = query.filter(Assessment.subject == subject)
    
    if term:
        query = query.filter(Assessment.term == term)
    
    if date_str:
        try:
            filter_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            query = query.filter(Assessment.date == filter_date)
        except ValueError:
            pass
    
    assessments = query.order_by(Assessment.date.desc(), Assessment.id.desc()).all()
    
    # Statistiques globales
    total_notes = Assessment.query.count()
    total_classes = Classe.query.count()
    total_subjects = db.session.query(Assessment.subject).distinct().count()
    notes_today = Assessment.query.filter(Assessment.date == date.today()).count()
    
    # Récapitulatif par type d'évaluation
    assessment_types_summary = {
        'interrogation': {'count': 0, 'average': 0},
        'devoir': {'count': 0, 'average': 0},
        'composition': {'count': 0, 'average': 0}
    }
    
    for atype in assessment_types_summary.keys():
        type_assessments = Assessment.query.filter_by(assessment_type=atype).all()
        assessment_types_summary[atype]['count'] = len(type_assessments)
        if type_assessments:
            avg = sum(a.normalized_score(20.0) for a in type_assessments) / len(type_assessments)
            assessment_types_summary[atype]['average'] = avg
    
    # Listes pour filtres
    classes = Classe.query.order_by(Classe.name).all()
    subjects_list = db.session.query(Assessment.subject).distinct().order_by(Assessment.subject).all()
    subjects_list = [s[0] for s in subjects_list if s[0]]
    
    return render_template(
        "notes/notes_management_dashboard.html",
        assessments=assessments,
        classes=classes,
        subjects=subjects_list,
        total_notes=total_notes,
        total_classes=total_classes,
        total_subjects=total_subjects,
        notes_today=notes_today,
        assessment_types_summary=assessment_types_summary,
        selected_class_id=class_id,
        selected_subject=subject,
        selected_term=term,
        selected_date=date_str
    )


# Alias pour compatibilité (route "/" redirige vers dashboard)
@notes_bp.route("/")
@login_required
def list_notes():
    """Redirige vers le tableau de bord (pour compatibilité)"""
    return redirect(url_for("notes.notes_dashboard"))


# --------------------------------------------------------
# SAISIE DES NOTES PAR CLASSE
# --------------------------------------------------------
@notes_bp.route("/entry", methods=["GET", "POST"])
@login_required
def notes_entry_by_class():
    """Interface de saisie des notes par classe"""
    form = BulkAssessmentForm()
    form.class_id.choices = [(c.id, c.name) for c in Classe.query.order_by(Classe.name).all()]
    
    students_data = []
    selected_class = None
    selected_subject = None
    selected_assessment_type = None
    selected_date = None
    selected_term = None
    selected_max_score = None
    
    if request.method == "POST":
        action = request.form.get("action", "")
        
        if action == "load_students":
            # Charger les élèves de la classe sélectionnée
            if form.validate_on_submit():
                class_id = form.class_id.data
                selected_class = Classe.query.get(class_id)
                selected_subject = form.subject.data
                selected_assessment_type = form.assessment_type.data
                selected_date = form.date.data.strftime("%Y-%m-%d") if form.date.data else date.today().strftime("%Y-%m-%d")
                selected_term = form.term.data
                selected_max_score = form.max_score.data
                
                # Récupérer les élèves de la classe
                students_data = Student.query.filter_by(class_id=class_id).order_by(Student.last_name).all()
        
        elif action == "save_notes":
            # Enregistrer les notes saisies
            class_id = int(request.form.get("class_id", 0))
            subject = request.form.get("subject", "")
            assessment_type = request.form.get("assessment_type", "")
            date_str = request.form.get("date", str(date.today()))
            note_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            term = int(request.form.get("term", 1))
            max_score = float(request.form.get("max_score", "20"))
            
            # Récupérer les élèves de la classe
            students = Student.query.filter_by(class_id=class_id).order_by(Student.last_name).all()
            
            # Traiter l'ajout des notes
            count = 0
            for student in students:
                score_key = f"score_{student.id}"
                if score_key in request.form:
                    try:
                        score = float(request.form[score_key])
                        if score > 0:  # N'enregistrer que si la note est saisie (> 0)
                            # Vérifier un doublon
                            exists = Assessment.query.filter_by(
                                student_id=student.id,
                                subject=subject,
                                assessment_type=assessment_type,
                                date=note_date,
                                term=term
                            ).first()
                            
                            if not exists:
                                assessment = Assessment(
                                    student_id=student.id,
                                    subject=subject,
                                    assessment_type=assessment_type,
                                    score=score,
                                    max_score=max_score,
                                    date=note_date,
                                    term=term
                                )
                                db.session.add(assessment)
                                count += 1
                    except (ValueError, TypeError):
                        pass
            
            if count > 0:
                db.session.commit()
                flash(f"✅ {count} note(s) enregistrée(s) avec succès !", "success")
                
                # Envoyer correspondance parent via le service
                ParentMessagingService.send_daily_notes(class_id, subject, note_date)
                
                return redirect(url_for("notes.notes_dashboard"))
            else:
                flash("❌ Aucune note valide n'a été saisie.", "danger")
    
    return render_template(
        "notes/notes_entry_by_class.html",
        form=form,
        students_data=students_data,
        selected_class=selected_class,
        selected_subject=selected_subject,
        selected_assessment_type=selected_assessment_type,
        selected_date=selected_date,
        selected_term=selected_term,
        selected_max_score=selected_max_score
    )


# Alias pour compatibilité
@notes_bp.route("/daily", methods=["GET", "POST"])
@login_required
def daily_entry():
    """Redirige vers notes_entry_by_class"""
    return redirect(url_for("notes.notes_entry_by_class"))


# --------------------------------------------------------
# AJOUTER UNE NOTE INDIVIDUELLE
# --------------------------------------------------------
@notes_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_note():
    """Ajouter une note individuelle pour un élève"""
    form = AssessmentForm()
    form.student_id.choices = [(s.id, s.full_name) for s in Student.query.all()]

    if form.validate_on_submit():
        note = Assessment(
            student_id=form.student_id.data,
            subject=form.subject.data,
            assessment_type=form.assessment_type.data,
            score=form.score.data,
            max_score=form.max_score.data,
            date=form.date.data or date.today(),
            term=form.term.data,
        )
        db.session.add(note)
        db.session.commit()
        flash("✅ Note ajoutée avec succès !", "success")
        
        # Envoyer message au(x) parent(s) via le service
        student = Student.query.get(form.student_id.data)
        ParentMessagingService.send_individual_note(student, note)
        
        return redirect(url_for("notes.list_notes"))

    return render_template("notes/notes_form.html", form=form)


# --------------------------------------------------------
# MODIFIER UNE NOTE
# --------------------------------------------------------
@notes_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
@admin_or_director_required
def edit_note(id):
    """Modifier une note existante"""
    note = Assessment.query.get_or_404(id)
    form = AssessmentForm()
    form.student_id.choices = [(s.id, s.full_name) for s in Student.query.all()]

    if form.validate_on_submit():
        note.student_id = form.student_id.data
        note.subject = form.subject.data
        note.assessment_type = form.assessment_type.data
        note.score = form.score.data
        note.max_score = form.max_score.data
        note.date = form.date.data or date.today()
        note.term = form.term.data
        
        db.session.commit()
        flash("✅ Note mise à jour avec succès !", "success")
        return redirect(url_for("notes.list_notes"))
    
    elif request.method == "GET":
        form.student_id.data = note.student_id
        form.subject.data = note.subject
        form.assessment_type.data = note.assessment_type
        form.score.data = note.score
        form.max_score.data = note.max_score
        form.date.data = note.date
        form.term.data = note.term

    return render_template("notes/notes_form.html", form=form, note=note)


# --------------------------------------------------------
# SUPPRIMER UNE NOTE
# --------------------------------------------------------
@notes_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
@admin_or_director_required
def delete_note(id):
    """Supprimer une note"""
    note = Assessment.query.get_or_404(id)
    db.session.delete(note)
    db.session.commit()
    flash("🗑️ Note supprimée", "info")
    return redirect(url_for("notes.list_notes"))


# --------------------------------------------------------
# BULLETIN TRIMESTRIEL
# --------------------------------------------------------
@notes_bp.route("/bulletin/<int:student_id>/<int:term>")
@login_required
def student_bulletin(student_id, term):
    """Affiche le bulletin d'un élève pour un trimestre"""
    student = Student.query.get_or_404(student_id)
    
    assessments = Assessment.query.filter_by(
        student_id=student_id,
        term=term
    ).order_by(Assessment.date, Assessment.subject).all()
    
    # Statistiques par matière
    subjects_stats = {}
    for assessment in assessments:
        if assessment.subject not in subjects_stats:
            subjects_stats[assessment.subject] = {
                'scores': [],
                'types': {}
            }
        subjects_stats[assessment.subject]['scores'].append(assessment.score)
        
        atype = assessment.assessment_type
        if atype not in subjects_stats[assessment.subject]['types']:
            subjects_stats[assessment.subject]['types'][atype] = []
        subjects_stats[assessment.subject]['types'][atype].append(assessment.score)
    
    # Calcul moyennes
    for subject, data in subjects_stats.items():
        data['average'] = sum(data['scores']) / len(data['scores']) if data['scores'] else 0
        for atype, scores in data['types'].items():
            data['types'][atype + '_avg'] = sum(scores) / len(scores) if scores else 0
    
    return render_template(
        "notes/bulletin.html",
        student=student,
        term=term,
        assessments=assessments,
        subjects_stats=subjects_stats
    )


# --------------------------------------------------------
# STATISTIQUES PAR CLASSE
# --------------------------------------------------------
@notes_bp.route("/stats/<int:class_id>/<int:term>")
@login_required
def class_stats(class_id, term):
    """Affiche les statistiques des notes pour une classe et un trimestre"""
    classe = Classe.query.get_or_404(class_id)
    
    assessments = Assessment.query.join(Student).filter(
        Student.class_id == class_id,
        Assessment.term == term
    ).all()
    
    if not assessments:
        flash("Aucune note pour cette classe/trimestre", "warning")
        return redirect(url_for("notes.list_notes"))
    
    # Statistiques globales
    avg_score = sum(a.score for a in assessments) / len(assessments)
    
    # Par matière
    subjects = {}
    for assessment in assessments:
        if assessment.subject not in subjects:
            subjects[assessment.subject] = []
        subjects[assessment.subject].append(assessment.score)
    
    for subject in subjects:
        subjects[subject] = {
            'average': sum(subjects[subject]) / len(subjects[subject]),
            'min': min(subjects[subject]),
            'max': max(subjects[subject]),
            'count': len(subjects[subject])
        }
    
    return render_template(
        "notes/class_stats.html",
        classe=classe,
        term=term,
        avg_score=avg_score,
        subjects=subjects,
        total_notes=len(assessments)
    )


# ========================================================
# CORRESPONDANCE WHATSAPP
# ========================================================

@notes_bp.route("/correspondence", methods=["GET", "POST"])
@login_required
def correspondence():
    """
    Tableau de bord de correspondance parent via WhatsApp
    Permet d'envoyer les notes du jour à tous les parents d'une classe
    """
    from sqlalchemy import and_
    

    classes = Classe.query.order_by(Classe.name).all()
    selected_class = None
    selected_date = None
    students_notes = []
    message_preview = ""
    personal_message_preview = ""
    personal_send_count = 0

    if request.method == "POST":
        class_id = request.form.get("class_id", type=int)
        date_str = request.form.get("date", type=str)
        action = request.form.get("action", type=str)
        selected_students_ids = request.form.getlist("selected_students")
        personal_message = request.form.get("personal_message", type=str)
        parent_ids = request.form.getlist("parent_ids")

        if class_id and date_str:
            selected_class = Classe.query.get(class_id)
            selected_date = date_str
            try:
                filter_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except Exception:
                filter_date = date.today()

            # Récupérer tous les élèves de la classe
            students = Student.query.filter_by(class_id=class_id).order_by(Student.last_name).all()
            # Pour chaque élève, récupérer ses notes du jour
            for student in students:
                notes = Assessment.query.filter_by(student_id=student.id, date=filter_date).order_by(Assessment.subject).all()
                if notes:
                    students_notes.append({
                        'id': student.id,
                        'name': student.full_name,
                        'notes': notes,
                        'parents': student.parents
                    })

            # Si action = send_notes, préparer et ouvrir WhatsApp Web pour chaque parent WhatsApp des élèves sélectionnés
            if action == "send_notes" and selected_students_ids:
                # Compter le nombre d'onglets à ouvrir
                total_to_open = 0
                for student in students_notes:
                    if str(student['id']) in selected_students_ids:
                        for parent in student['parents']:
                            if parent.whatsapp_optin and parent.phone_e164:
                                total_to_open += 1
                # Confirmation utilisateur
                from markupsafe import Markup
                if total_to_open > 1:
                    confirm_html = Markup(f"<script>if(!confirm('Vous allez ouvrir {total_to_open} onglets WhatsApp. Continuer ?')){{window.history.back();}}</script>")
                    flash(confirm_html, "info")
                else:
                    import urllib.parse, webbrowser
                    for student in students_notes:
                        if str(student['id']) in selected_students_ids:
                            notes_text = ""
                            for note in student['notes']:
                                notes_text += f"{note.subject} : {note.score}/{note.max_score} ({note.assessment_type_display})\n"
                            message = (
                                "Bonjour chers Parents,\n"
                                f"Votre enfant *{student['name']}* a reçu ces notes aujourd'hui :\n\n"
                                f"{notes_text}\n"
                                "Nous vous prions de signer ces notes pour demain afin d’éviter toute sanction disciplinaire.\n"
                                "*CS LE ROCHER*."
                            )
                            for parent in student['parents']:
                                if parent.whatsapp_optin and parent.phone_e164:
                                    msg_encoded = urllib.parse.quote(message)
                                    url = f"https://web.whatsapp.com/send?phone={parent.phone_e164}&text={msg_encoded}"
                                    webbrowser.open(url, new=0)
                    flash("Brouillon WhatsApp ouvert pour l'élève sélectionné.", "success")

    # Récupérer les matières disponibles
    subjects = db.session.query(Assessment.subject).distinct().order_by(Assessment.subject).all()
    subjects = [s[0] for s in subjects if s[0]]
    # Liste de tous les parents (pour envoi personnalisé)
    parents = Parent.query.order_by(Parent.last_name, Parent.first_name).all()
    # Liste de tous les élèves (pour message personnalisé)
    students = Student.query.order_by(Student.last_name, Student.first_name).all()

    # --- Envoi personnalisé à un ou plusieurs parents ---
    if request.method == "POST" and action in ("personal_preview", "personal_send"):
        # Déterminer la liste des parents ciblés
        targets = []
        student_ids = request.form.getlist("student_ids")
        if parent_ids:
            # parent_ids contient des ids de parents sélectionnés
            for pid in parent_ids:
                p = Parent.query.get(int(pid))
                if p:
                    targets.append(p)
        elif student_ids:
            # Si des élèves sont sélectionnés, prendre leurs parents WhatsApp
            for sid in student_ids:
                student = Student.query.get(int(sid))
                if student:
                    for p in student.parents:
                        if p.whatsapp_optin and p.phone_e164:
                            targets.append(p)
        elif class_id:
            # si class_id donné, prendre tous les parents WhatsApp de la classe
            students = Student.query.filter_by(class_id=class_id).all()
            for s in students:
                for p in s.parents:
                    if p.whatsapp_optin and p.phone_e164:
                        targets.append(p)

        # Nettoyer la liste (unique)
        unique_targets = {}
        for p in targets:
            if p and p.id not in unique_targets:
                unique_targets[p.id] = p
        targets = list(unique_targets.values())

        if action == "personal_preview":
            personal_message_preview = personal_message or ""

        elif action == "personal_send":
            if not personal_message:
                flash("Le message personnalisé est vide.", "warning")
            else:
                import urllib.parse, webbrowser
                total_to_open = 0
                for parent in targets:
                    if parent.whatsapp_optin and parent.phone_e164:
                        msg_encoded = urllib.parse.quote(personal_message)
                        url = f"https://web.whatsapp.com/send?phone={parent.phone_e164}&text={msg_encoded}"
                        webbrowser.open(url, new=0)
                        total_to_open += 1
                if total_to_open > 0:
                    flash(f"Brouillon WhatsApp ouvert pour {total_to_open} parent(s) sélectionné(s).", "success")
                else:
                    flash("Aucun parent WhatsApp valide sélectionné.", "warning")

    return render_template(
        "notes/correspondence.html",
        classes=classes,
        subjects=subjects,
        parents=parents,
        selected_class=selected_class,
        selected_date=selected_date,
        students_notes=students_notes,
        message_preview=message_preview,
        personal_message_preview=personal_message_preview,
        personal_send_count=personal_send_count,
        students=students
    )


# ========================================================
# API POUR AFFICHAGE DYNAMIQUE
# ========================================================

@notes_bp.route("/api/students-by-class/<int:class_id>")
@login_required
def api_students_by_class(class_id):
    """Retourne la liste des élèves d'une classe en JSON"""
    students = Student.query.filter_by(class_id=class_id).order_by(Student.last_name).all()
    return jsonify([{
        'id': s.id,
        'full_name': s.full_name
    } for s in students])

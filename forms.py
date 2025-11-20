from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    StringField,
    PasswordField,
    SubmitField,
    SelectField,
    FloatField,
    IntegerField,
    DateField
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo,
    Optional,
    NumberRange,
    ValidationError
)

# Formulaire d'inscription utilisateur
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(check_deliverability=False)])
    password = PasswordField(
        "Mot de passe",
        validators=[DataRequired(), Length(min=6, message="Le mot de passe doit contenir au moins 6 caractères")]
    )
    confirm = PasswordField(
        "Confirmer le mot de passe",
        validators=[DataRequired(), EqualTo("password", message="Les mots de passe ne correspondent pas.")]
    )
    submit = SubmitField("Créer le compte")


# Formulaire de connexion
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(check_deliverability=False), Length(max=150)])
    password = PasswordField("Mot de passe", validators=[DataRequired(), Length(min=6, max=128)])
    submit = SubmitField("Se connecter")


# Formulaire admin pour gérer un utilisateur
class UserForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(check_deliverability=False), Length(max=150)])
    name = StringField("Nom complet", validators=[Optional(), Length(max=150)])
    password = PasswordField(
        "Mot de passe (laisser vide pour ne pas changer)",
        validators=[Optional(), Length(min=6, max=128)]
    )
    role = SelectField(
        "Rôle",
        choices=[
            ("teacher", "Enseignant"),
            ("admin", "Administrateur")
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField("Enregistrer")


# Formulaire élève
class StudentForm(FlaskForm):
    first_name = StringField("Prénom", validators=[DataRequired(), Length(max=120)])
    last_name = StringField("Nom", validators=[DataRequired(), Length(max=120)])
    birthdate = DateField("Date de naissance", validators=[Optional()])

    class_id = SelectField(
        "Classe",
        choices=[],  # Les choix sont définis dynamiquement dans la route
        validators=[DataRequired()]
    )
    

    # -------- PARENT --------
    parent_first_name = StringField("Prénom du parent", validators=[Optional(), Length(max=120)])
    parent_last_name = StringField("Nom du parent", validators=[Optional(), Length(max=120)])
    parent_phone = StringField("Téléphone (E.164)", validators=[Optional(), Length(max=30)])
    parent_whatsapp = BooleanField("Parent inscrit sur WhatsApp")

    submit = SubmitField("Enregistrer")

    def validate_parent_phone(self, field):
        if field.data:
            if not field.data.startswith("+") or not field.data[1:].isdigit():
                raise ValidationError("Format invalide. Exemple : +22997000000")


class DeleteForm(FlaskForm):
    submit = SubmitField("Supprimer")


# Formulaire parent
class ParentForm(FlaskForm):
    first_name = StringField("Prénom", validators=[Optional(), Length(max=120)])
    last_name = StringField("Nom", validators=[Optional(), Length(max=120)])
    phone_e164 = StringField("Téléphone (format E.164)", validators=[Optional(), Length(max=30)])
    whatsapp_optin = BooleanField("Opt-in WhatsApp")
    submit = SubmitField("Enregistrer")

    def validate_phone_e164(self, field):
        if field.data:
            if not field.data.startswith("+") or not field.data[1:].isdigit():
                raise ValidationError("Le numéro doit être en format E.164, ex: +229xxxxxxxx")


# Formulaire note / évaluation
class AssessmentForm(FlaskForm):
    student_id = SelectField("Élève", coerce=int, validators=[DataRequired()])
    subject = StringField("Matière", validators=[DataRequired(), Length(max=120)])
    score = FloatField("Note obtenue", validators=[DataRequired(), NumberRange(min=0)])
    max_score = FloatField("Note maximale", default=20.0, validators=[DataRequired(), NumberRange(min=0.1)])
    
    # Type de note : interrogation, devoir, composition
    assessment_type = SelectField(
        "Type de note",
        choices=[
            ('interrogation', '❓ Interrogation (5-6 par jour)'),
            ('devoir', '📝 Devoir (1 par jour)'),
            ('composition', '📋 Composition (1 par trimestre)')
        ],
        validators=[DataRequired()]
    )
    
    date = DateField("Date de l'évaluation", validators=[Optional()])
    term = IntegerField("Trimestre (1-3)", validators=[DataRequired(), NumberRange(min=1, max=3)])
    submit = SubmitField("Ajouter la note")


# Formulaire saisie en masse pour une classe (même jour, même matière, plusieurs élèves)
class BulkAssessmentForm(FlaskForm):
    class_id = SelectField("Classe", coerce=int, validators=[DataRequired()])
    subject = SelectField(
        "Matière",
        choices=[
            ("Comunication écrite", "Comunication écrite"),
            ("Lecture", "Lecture"),
            ("Français", "Français"),
            ("Histoire et géographie", "Histoire et géographie"),
            ("Anglais", "Anglais"),
            ("SVT", "SVT"),
            ("PCT", "PCT"),
            ("Mathématique", "Mathématique"),
            ("Espagnole", "Espagnole"),
            ("Philosophie", "Philosophie")
        ],
        validators=[DataRequired()]
    )
    
    assessment_type = SelectField(
        "Type de note",
        choices=[
            ('interrogation', '❓ Interrogation'),
            ('devoir', '📝 Devoir'),
            ('composition', '📋 Composition')
        ],
        validators=[DataRequired()]
    )
    
    date = DateField("Date", validators=[Optional()])
    term = IntegerField("Trimestre (1-3)", validators=[DataRequired(), NumberRange(min=1, max=3)])
    max_score = FloatField("Note maximale (défaut: 20.0)", default=20.0, validators=[DataRequired(), NumberRange(min=0.1)])
    
    submit = SubmitField("Saisir les notes")

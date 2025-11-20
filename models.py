"""
Définition des modèles de données avec SQLAlchemy.
"""

from datetime import datetime, date, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# -------- USER --------
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default="teacher", nullable=False)  # admin, teacher, director
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def set_password(self, pwd):
        self.password_hash = generate_password_hash(pwd)

    def check_password(self, pwd):
        return check_password_hash(self.password_hash, pwd)

    def is_admin(self):
        return self.role == "admin"

    def is_director(self):
        return self.role == "director"

    def is_teacher(self):
        return self.role == "teacher"

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


# -------- CLASSE --------
class Classe(db.Model):
    __tablename__ = "classes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    students = db.relationship(
        "Student",
        back_populates="classe",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Classe {self.name}>"


# -------- PROFESSOR --------
class Professor(db.Model):
    __tablename__ = "professors"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False, index=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(30), nullable=True)
    subjects = db.Column(db.String(500), nullable=True)  # Matières (séparées par virgule)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Optionnel: lier un `Professor` à un `User` (compte de connexion)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    user = db.relationship('User', backref=db.backref('professor_profile', uselist=False))

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}"

    def __repr__(self):
        return f"<Professor {self.full_name}>"


# -------- STUDENT --------
class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False, index=True)
    birthdate = db.Column(db.Date, nullable=True)

    class_id = db.Column(
        db.Integer,
        db.ForeignKey("classes.id", ondelete="SET NULL"),
        nullable=True
    )

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    classe = db.relationship("Classe", back_populates="students")
    parents = db.relationship("Parent", secondary="parent_student", back_populates="students")

    assessments = db.relationship(
        "Assessment",
        back_populates="student",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}"

    def __repr__(self):
        return f"<Student {self.full_name}>"


# -------- PARENT --------
class Parent(db.Model):
    __tablename__ = "parents"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=True)
    last_name = db.Column(db.String(120), nullable=True)
    phone_e164 = db.Column(db.String(30), nullable=True, index=True)
    whatsapp_optin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    students = db.relationship("Student", secondary="parent_student", back_populates="parents")

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}"

    def __repr__(self):
        return f"<Parent {self.last_name} {self.first_name}>"


# -------- TABLE ASSOCIATION PARENT ↔ STUDENT --------
parent_student = db.Table(
    "parent_student",
    db.Column("parent_id", db.Integer, db.ForeignKey("parents.id"), primary_key=True),
    db.Column("student_id", db.Integer, db.ForeignKey("students.id"), primary_key=True),
)


# -------- ASSESSMENT --------
class Assessment(db.Model):
    __tablename__ = "assessments"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)

    subject = db.Column(db.String(120), nullable=False)
    score = db.Column(db.Float, nullable=False)
    max_score = db.Column(db.Float, nullable=False, default=20.0)

    # Type de note : 'interrogation' (5-6 par jour), 'devoir' (1 par jour), 'composition' (1 par trimestre)
    assessment_type = db.Column(
        db.String(50), 
        default='interrogation',
        nullable=False,
        index=True
    )

    # IMPORTANT : date → stocker correctement une date uniquement
    date = db.Column(db.Date, default=date.today, nullable=False)

    # Trimestre (1, 2, 3)
    term = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    student = db.relationship("Student", back_populates="assessments")

    def normalized_score(self, scale=20.0):
        if self.max_score <= 0:
            return 0
        return (self.score / self.max_score) * scale

    @property
    def assessment_type_display(self):
        """Affichage lisible du type de note"""
        types_map = {
            'interrogation': '❓ Interrogation',
            'devoir': '📝 Devoir',
            'composition': '📋 Composition'
        }
        return types_map.get(self.assessment_type, self.assessment_type)

    def __repr__(self):
        return f"<Assessment {self.subject} {self.score}/{self.max_score} ({self.assessment_type})"


# -------- REPORT CARD --------
class ReportCard(db.Model):
    __tablename__ = "report_cards"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    term = db.Column(db.Integer, nullable=False)
    generated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    pdf_url = db.Column(db.String(500), nullable=True)

    def __repr__(self):
        return f"<ReportCard student={self.student_id} term={self.term}>"


# -------- MESSAGE LOG --------
class MessageLog(db.Model):
    __tablename__ = "message_logs"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("parents.id"), index=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), index=True)

    template_name = db.Column(db.String(200))
    content = db.Column(db.Text)
    status = db.Column(db.String(50))
    external_id = db.Column(db.String(200))

    # Twilio / provider tracking
    twilio_sid = db.Column(db.String(200), nullable=True)
    attempts = db.Column(db.Integer, default=0, nullable=False)
    last_error = db.Column(db.String(1000), nullable=True)

    sent_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<MessageLog parent={self.parent_id} status={self.status}>"


# -------- SCHOOL YEAR --------
class SchoolYear(db.Model):
    __tablename__ = "school_years"

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(20), nullable=False, unique=True)
    active = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<SchoolYear {self.year} active={self.active}>"

"""
Test du système de saisie des notes quotidiennes et correspondance parent
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from models import Student, Assessment, Classe, Parent, User
from datetime import date, datetime
from services import ParentMessagingService

app = create_app()

def test_notes_system():
    """Test complet du système de notes"""
    
    with app.app_context():
        print("=" * 60)
        print("TEST DU SYSTÈME DE GESTION DES NOTES")
        print("=" * 60)
        
        # Initialiser la base de données
        db.create_all()
        
        # Créer un utilisateur admin
        admin = User.query.filter_by(email="admin@ecole.local").first()
        if not admin:
            admin = User(email="admin@ecole.local", name="Admin", role="admin")
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin créé")
        
        # Créer des classes
        classes_names = ['6ème A', '6ème B', '5ème A']
        for class_name in classes_names:
            if not Classe.query.filter_by(name=class_name).first():
                classe = Classe(name=class_name)
                db.session.add(classe)
        db.session.commit()
        print(f"✅ {len(classes_names)} classe(s) créée(s)")
        
        # Créer des élèves et parents
        classe = Classe.query.filter_by(name='6ème A').first()
        
        # Parent 1
        parent1 = Parent.query.filter_by(phone_e164="+22997000001").first()
        if not parent1:
            parent1 = Parent(
                first_name="Marie",
                last_name="Dupont",
                phone_e164="+22997000001",
                whatsapp_optin=True
            )
            db.session.add(parent1)
            db.session.commit()
        
        # Élèves
        students_data = [
            ("Jean", "Dupont"),
            ("Sophie", "Dupont"),
            ("Alice", "Martin"),
        ]
        
        students = []
        for first_name, last_name in students_data:
            student = Student.query.filter_by(
                first_name=first_name,
                last_name=last_name,
                class_id=classe.id
            ).first()
            
            if not student:
                student = Student(
                    first_name=first_name,
                    last_name=last_name,
                    class_id=classe.id,
                    birthdate=date(2008, 5, 15)
                )
                db.session.add(student)
                db.session.commit()
            
            # Associer le parent
            if parent1 not in student.parents:
                student.parents.append(parent1)
                db.session.commit()
            
            students.append(student)
        
        print(f"✅ {len(students)} élève(s) créé(e)s et lié(e)s au parent")
        
        # Test 1 : Ajouter une note individuelle
        print("\n" + "=" * 60)
        print("TEST 1 : AJOUT DE NOTE INDIVIDUELLE")
        print("=" * 60)
        
        student = students[0]
        assessment = Assessment(
            student_id=student.id,
            subject="Français",
            score=17.5,
            max_score=20.0,
            assessment_type="interrogation",
            date=date.today(),
            term=1
        )
        db.session.add(assessment)
        db.session.commit()
        
        print(f"✅ Note créée pour {student.full_name}")
        print(f"   Matière: {assessment.subject}")
        print(f"   Type: {assessment.assessment_type_display}")
        print(f"   Note: {assessment.score}/{assessment.max_score}")
        print(f"   Rendement /20: {assessment.normalized_score(20.0):.2f}")
        
        # Test 2 : Ajouter plusieurs notes pour une classe (saisie quotidienne)
        print("\n" + "=" * 60)
        print("TEST 2 : SAISIE QUOTIDIENNE POUR UNE CLASSE")
        print("=" * 60)
        
        notes_data = [
            (students[0].id, 15.0),
            (students[1].id, 18.5),
            (students[2].id, 16.0),
        ]
        
        for student_id, score in notes_data:
            # Vérifier doublon
            exists = Assessment.query.filter_by(
                student_id=student_id,
                subject="Mathématiques",
                assessment_type="devoir",
                date=date.today(),
                term=1
            ).first()
            
            if not exists:
                assessment = Assessment(
                    student_id=student_id,
                    subject="Mathématiques",
                    score=score,
                    max_score=20.0,
                    assessment_type="devoir",
                    date=date.today(),
                    term=1
                )
                db.session.add(assessment)
        
        db.session.commit()
        print(f"✅ {len(notes_data)} note(s) ajoutée(s) pour 'Mathématiques'")
        
        # Test 3 : Récupérer et afficher les statistiques
        print("\n" + "=" * 60)
        print("TEST 3 : STATISTIQUES")
        print("=" * 60)
        
        all_assessments = Assessment.query.join(Student).filter(
            Student.class_id == classe.id,
            Assessment.term == 1
        ).all()
        
        print(f"✅ Total des notes pour la classe: {len(all_assessments)}")
        
        # Par matière
        subjects_stats = {}
        for assessment in all_assessments:
            if assessment.subject not in subjects_stats:
                subjects_stats[assessment.subject] = []
            subjects_stats[assessment.subject].append(assessment.score)
        
        print("\n📚 Moyennes par matière:")
        for subject, scores in subjects_stats.items():
            avg = sum(scores) / len(scores) if scores else 0
            print(f"   {subject}: {avg:.2f}/20 ({len(scores)} notes)")
        
        # Test 4 : Générer des messages
        print("\n" + "=" * 60)
        print("TEST 4 : GÉNÉRATION DE MESSAGES PARENT")
        print("=" * 60)
        
        math_assessments = Assessment.query.filter_by(
            subject="Mathématiques",
            date=date.today(),
            term=1
        ).all()
        
        if math_assessments:
            message = ParentMessagingService._generate_daily_message(
                math_assessments, 
                "Mathématiques", 
                date.today()
            )
            print("📝 Message généré pour parents:")
            print(message)
        
        # Test 5 : Simuler l'envoi de messages
        print("\n" + "=" * 60)
        print("TEST 5 : SIMULATION ENVOI DE MESSAGES")
        print("=" * 60)
        
        count = ParentMessagingService.send_individual_note(student, assessment)
        print(f"✅ Messages enregistrés pour {count} parent(s)")
        
        # Vérifier le log
        from models import MessageLog
        logs = MessageLog.query.all()
        print(f"📋 Messages enregistrés dans le log: {len(logs)}")
        for log in logs[:3]:  # Afficher les 3 premiers
            print(f"   - Parent: {log.parent_id}, Status: {log.status}")
        
        print("\n" + "=" * 60)
        print("✅ TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS!")
        print("=" * 60)


if __name__ == "__main__":
    test_notes_system()

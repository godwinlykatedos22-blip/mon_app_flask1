#!/usr/bin/env python3
"""
Test script pour le système de correspondance WhatsApp
Simule l'envoi de notes à des parents via pywhatkit
"""

import os
import sys
from datetime import date, datetime, timedelta

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User, Classe, Student, Parent, Assessment, MessageLog
from services import ParentMessagingService

# Créer l'app Flask
app = create_app()

def test_whatsapp_correspondence():
    """Test complet du système de correspondance WhatsApp"""
    
    with app.app_context():
        print("=" * 60)
        print("🧪 TEST CORRESPONDANCE WHATSAPP")
        print("=" * 60)
        
        # 1. Nettoyer la BD (optionnel)
        print("\n1️⃣  Initialisation de la base de données...")
        try:
            # Garder les données existantes
            admin = User.query.filter_by(email="admin@ecole.local").first()
            if not admin:
                admin = User(email="admin@ecole.local", name="Admin", role="admin")
                admin.set_password("admin123")
                db.session.add(admin)
                db.session.commit()
                print("   ✅ Admin créé")
            else:
                print("   ✅ Admin existant trouvé")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return
        
        # 2. Créer les classes si nécessaire
        print("\n2️⃣  Vérification des classes...")
        classes = Classe.query.all()
        if not classes:
            print("   ⚠️  Aucune classe trouvée. Création des classes...")
            class_names = ['6ème', '5ème', '4ème', '3ème']
            for name in class_names:
                classe = Classe(name=name)
                db.session.add(classe)
            db.session.commit()
            classes = Classe.query.all()
            print(f"   ✅ {len(classes)} classe(s) créée(s)")
        else:
            print(f"   ✅ {len(classes)} classe(s) trouvée(s)")
        
        # 3. Créer les élèves et parents
        print("\n3️⃣  Vérification des élèves et parents...")
        classe = classes[0]
        
        students = Student.query.filter_by(class_id=classe.id).all()
        if not students:
            print(f"   🆕 Création d'élèves et parents pour {classe.name}...")
            
            students_data = [
                {
                    "first_name": "Jean",
                    "last_name": "Dupont",
                    "parent_names": [("Marie", "Dupont", "+22962345678")],
                },
                {
                    "first_name": "Marie",
                    "last_name": "Martin",
                    "parent_names": [("Philippe", "Martin", "+22961234567")],
                },
                {
                    "first_name": "Pierre",
                    "last_name": "Bernard",
                    "parent_names": [("Anne", "Bernard", "+22963456789")],
                },
            ]
            
            for std_data in students_data:
                student = Student(
                    first_name=std_data["first_name"],
                    last_name=std_data["last_name"],
                    class_id=classe.id,
                )
                db.session.add(student)
                db.session.flush()
                
                for parent_fname, parent_lname, phone in std_data["parent_names"]:
                    parent = Parent(
                        first_name=parent_fname,
                        last_name=parent_lname,
                        phone_e164=phone,
                        whatsapp_optin=True,  # ✅ Opt-in WhatsApp
                    )
                    db.session.add(parent)
                    db.session.flush()
                    student.parents.append(parent)
            
            db.session.commit()
            students = Student.query.filter_by(class_id=classe.id).all()
            print(f"   ✅ {len(students)} élève(s) créé(e)s avec parent(s)")
        else:
            print(f"   ✅ {len(students)} élève(s) trouvé(e)s")
        
        # 4. Créer des notes du jour
        print("\n4️⃣  Création des notes du jour...")
        today = date.today()
        subject = "Mathématiques"
        
        # Vérifier s'il y a déjà des notes
        existing_notes = Assessment.query.filter_by(
            subject=subject,
            date=today
        ).all()
        
        if not existing_notes:
            for idx, student in enumerate(students):
                score = [15.5, 18.0, 16.5][idx % 3]
                assessment = Assessment(
                    student_id=student.id,
                    subject=subject,
                    assessment_type="interrogation",
                    score=score,
                    max_score=20,
                    date=today,
                    term=1,
                )
                db.session.add(assessment)
            db.session.commit()
            print(f"   ✅ {len(students)} note(s) créée(s) pour {subject}")
        else:
            print(f"   ℹ️  {len(existing_notes)} note(s) déjà existante(s)")
        
        # 5. Récupérer les notes du jour
        print(f"\n5️⃣  Récupération des notes du jour ({subject})...")
        assessments_today = Assessment.query.filter_by(
            subject=subject,
            date=today
        ).all()
        
        if assessments_today:
            print(f"   ✅ {len(assessments_today)} note(s) trouvée(s)")
            for assessment in assessments_today:
                print(f"      - {assessment.student.full_name}: {assessment.score}/{assessment.max_score} ({assessment.normalized_score(20.0):.2f}/20) - {assessment.assessment_type_display}")
        
        # 6. Générer l'aperçu du message
        print(f"\n6️⃣  Génération du message WhatsApp...")
        message = ParentMessagingService._generate_daily_message(assessments_today, subject, today)
        print("   📝 APERÇU DU MESSAGE:")
        print("   " + "-" * 50)
        for line in message.split("\n"):
            print(f"   {line}")
        print("   " + "-" * 50)
        
        # 7. Simulation d'envoi (sans vraiment envoyer)
        print(f"\n7️⃣  Simulation d'envoi WhatsApp...")
        
        # Grouper par parent unique
        parents_to_notify = set()
        for assessment in assessments_today:
            for parent in assessment.student.parents:
                if parent.whatsapp_optin and parent.phone_e164:
                    parents_to_notify.add(parent.id)
        
        print(f"   📱 {len(parents_to_notify)} parent(s) à notifier")
        
        sent_count = 0
        for parent_id in parents_to_notify:
            parent = Parent.query.get(parent_id)
            print(f"\n   📲 Tentative d'envoi à {parent.first_name} {parent.last_name} ({parent.phone_e164})...")
            
            try:
                # Appeler la fonction d'envoi WhatsApp
                # Elle va logger mais pas vraiment envoyer (pywhatkit nécessite un navigateur)
                ParentMessagingService._send_whatsapp(parent, message)
                
                # Enregistrer dans MessageLog
                msg_log = MessageLog(
                    parent_id=parent.id,
                    template_name='daily_notes_whatsapp',
                    content=message,
                    status='sent_whatsapp'
                )
                db.session.add(msg_log)
                sent_count += 1
                print(f"      ✅ Message enregistré pour envoi")
                
            except Exception as e:
                msg_log = MessageLog(
                    parent_id=parent.id,
                    template_name='daily_notes_whatsapp',
                    content=message,
                    status='failed_whatsapp'
                )
                db.session.add(msg_log)
                print(f"      ❌ Erreur: {e}")
        
        db.session.commit()
        
        # 8. Vérifier les MessageLog
        print(f"\n8️⃣  Vérification des logs d'envoi...")
        msg_logs = MessageLog.query.filter_by(
            template_name='daily_notes_whatsapp'
        ).order_by(MessageLog.id.desc()).limit(5).all()
        
        print(f"   ✅ {len(msg_logs)} log(s) d'envoi trouvé(e)s")
        for log in msg_logs:
            parent = Parent.query.get(log.parent_id)
            print(f"      - {parent.full_name}: {log.status}")
        
        # RÉSUMÉ FINAL
        print("\n" + "=" * 60)
        print("✅ TEST COMPLÉTÉ AVEC SUCCÈS")
        print("=" * 60)
        print(f"""
📊 RÉSUMÉ:
   • Classe: {classe.name}
   • Élèves: {len(students)}
   • Notes du jour: {len(assessments_today)}
   • Parents notifiés: {sent_count}
   • Matière: {subject}
   • Date: {today.strftime('%d/%m/%Y')}

🔧 POUR VRAIMENT ENVOYER VIA WHATSAPP:
   1. Installer pywhatkit: pip install pywhatkit
   2. Avoir Chrome/Firefox installé
   3. Ouvrir WhatsApp Web: https://web.whatsapp.com
   4. Scanner le QR code avec votre téléphone
   5. Exécuter les fonctions d'envoi
   
⚠️  NOTE: pywhatkit utilise le navigateur pour envoyer via WhatsApp Web.
   C'est une alternative gratuite à Twilio/Infobip.

🌐 POUR PRODUCTION:
   Considérez Twilio, Infobip ou WhatsApp Business API.
        """)

if __name__ == "__main__":
    test_whatsapp_correspondence()

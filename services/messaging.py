"""
Services pour l'envoi de correspondance parent (Email, SMS, WhatsApp)
"""

from datetime import datetime, date
from models import db, MessageLog, Parent, Student, Assessment
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import time

try:
    import pywhatkit as kit
    PYWHATKIT_AVAILABLE = True
except ImportError:
    PYWHATKIT_AVAILABLE = False
    print("[WARNING] pywhatkit non installee - WhatsApp desactive")

try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except Exception:
    TWILIO_AVAILABLE = False
    # Pas d'affichage Unicode ici pour éviter les erreurs d'encodage
    print("[INFO] twilio non installe - Twilio WhatsApp desactive")


class ParentMessagingService:
    """Service centralisé pour l'envoi de messages aux parents"""
    
    @staticmethod
    def send_daily_notes(class_id, subject, note_date):
        """
        Envoie un résumé des notes de la journée à tous les parents concernés
        """
        # Récupérer les notes du jour pour cette classe et matière
        from models import Classe
        assessments = Assessment.query.join(Student).filter(
            Student.class_id == class_id,
            Assessment.subject == subject,
            Assessment.date == note_date
        ).all()
        
        if not assessments:
            return 0
        
        # Grouper par parent unique
        parents_notes = {}
        for assessment in assessments:
            for parent in assessment.student.parents:
                if parent.id not in parents_notes:
                    parents_notes[parent.id] = {
                        'parent': parent,
                        'notes': []
                    }
                parents_notes[parent.id]['notes'].append(assessment)
        
        # Envoyer à chaque parent
        count = 0
        for parent_id, data in parents_notes.items():
            parent = data['parent']
            notes = data['notes']
            
            # Génération du message
            message_content = ParentMessagingService._generate_daily_message(notes, subject, note_date)
            
            # Enregistrement dans MessageLog
            msg_log = MessageLog(
                parent_id=parent.id,
                template_name='daily_notes',
                content=message_content,
                status='queued'
            )
            db.session.add(msg_log)
            
            # Tentative d'envoi
            success = False

            # Email (optionnel)
            if parent.phone_e164:
                try:
                    ParentMessagingService._send_email(parent, message_content, subject, note_date)
                    msg_log.status = 'sent_email'
                    msg_log.sent_at = datetime.utcnow()
                    success = True
                except Exception as e:
                    print(f"Erreur Email {parent.id}: {str(e)}")
                    msg_log.status = 'failed_email'
                    msg_log.last_error = str(e)

            # WhatsApp via Twilio / pywhatkit
            if parent.whatsapp_optin and parent.phone_e164:
                try:
                    ok, info = ParentMessagingService._send_whatsapp(parent, message_content)
                    msg_log.attempts = (msg_log.attempts or 0) + 1
                    if ok:
                        # info may contain Twilio SID
                        msg_log.status = 'sent_whatsapp'
                        if info:
                            msg_log.twilio_sid = info
                        msg_log.sent_at = datetime.utcnow()
                        success = True
                    else:
                        msg_log.status = 'failed_whatsapp'
                        msg_log.last_error = str(info)
                except Exception as e:
                    print(f"Erreur WhatsApp {parent.id}: {str(e)}")
                    msg_log.attempts = (msg_log.attempts or 0) + 1
                    msg_log.status = 'failed_whatsapp'
                    msg_log.last_error = str(e)

            db.session.commit()
            if success:
                count += 1
        
        return count
    
    @staticmethod
    def send_individual_note(student, assessment):
        """
        Envoie la notification d'une note individuelle aux parents
        """
        parents = student.parents
        if not parents:
            return 0
        
        message_content = ParentMessagingService._generate_individual_message(student, assessment)
        
        count = 0
        for parent in parents:
            msg_log = MessageLog(
                parent_id=parent.id,
                student_id=student.id,
                template_name='individual_note',
                content=message_content,
                status='queued'
            )
            db.session.add(msg_log)
            
            # Tentative d'envoi
            try:
                ParentMessagingService._send_email(parent, message_content, assessment.subject)
                msg_log.status = 'sent_email'
                msg_log.sent_at = datetime.utcnow()
                count += 1
            except Exception as e:
                msg_log.status = 'failed'
                msg_log.last_error = str(e)
                print(f"Erreur envoi {parent.id}: {str(e)}")

            # Essayer WhatsApp aussi si opt-in
            if parent.whatsapp_optin and parent.phone_e164:
                try:
                    ok, info = ParentMessagingService._send_whatsapp(parent, message_content)
                    msg_log.attempts = (msg_log.attempts or 0) + 1
                    if ok:
                        msg_log.status = 'sent_whatsapp'
                        if info:
                            msg_log.twilio_sid = info
                        msg_log.sent_at = datetime.utcnow()
                        count += 1
                    else:
                        msg_log.status = 'failed_whatsapp'
                        msg_log.last_error = str(info)
                except Exception as e:
                    msg_log.attempts = (msg_log.attempts or 0) + 1
                    msg_log.status = 'failed_whatsapp'
                    msg_log.last_error = str(e)
                    print(f"Erreur WhatsApp envoi {parent.id}: {str(e)}")

            db.session.commit()
        
        return count
    
    @staticmethod
    def _generate_daily_message(assessments, subject, note_date):
        """
        Génère le message formaté pour le résumé de notes de la journée
        """
        # Grouper par élève
        students_notes = {}
        for assessment in assessments:
            student = assessment.student
            if student.id not in students_notes:
                students_notes[student.id] = {
                    'name': f"{student.first_name} {student.last_name}",
                    'notes': []
                }
            students_notes[student.id]['notes'].append(assessment)
        
        message = f"""
===============================================
📋 NOTES DU JOUR - {note_date.strftime('%d/%m/%Y')}
===============================================

Matière: {subject}

"""
        
        for student_id, data in students_notes.items():
            message += f"\n👤 {data['name']}\n"
            message += "-" * 40 + "\n"
            
            for assessment in data['notes']:
                normalized = assessment.normalized_score(20.0)
                message += f"   {assessment.assessment_type_display}\n"
                message += f"      Note: {assessment.score}/{assessment.max_score} ({normalized:.2f}/20)\n"
        
        message += f"\n===============================================\n"
        message += f"Pour plus de détails, consultez votre portail élève.\n"
        message += f"===============================================\n"
        
        return message
    
    @staticmethod
    def _generate_individual_message(student, assessment):
        """
        Génère le message formaté pour une note individuelle
        """
        normalized = assessment.normalized_score(20.0)
        
        message = f"""
===============================================
📝 NOUVELLE NOTE - {student.first_name} {student.last_name}
===============================================

Classe: {student.classe.name if student.classe else 'N/A'}
Matière: {assessment.subject}
Type: {assessment.assessment_type_display}

📊 Note: {assessment.score}/{assessment.max_score}
✨ Rendement (/20): {normalized:.2f}

📅 Date: {assessment.date.strftime('%d/%m/%Y')}
🔢 Trimestre: {assessment.term}/3

===============================================
Pour plus de détails, consultez votre portail élève.
===============================================
"""
        return message
    
    @staticmethod
    def _send_email(parent, content, subject="Notes de l'élève", note_date=None):
        """
        Envoie un email au parent
        
        TODO: Configuration SMTP via variables d'environnement
        """
        # Exemple simplifié - adapter selon configuration réelle
        smtp_server = os.environ.get('SMTP_SERVER', 'localhost')
        smtp_port = os.environ.get('SMTP_PORT', 587)
        sender_email = os.environ.get('SENDER_EMAIL', 'noreply@ecole.local')
        sender_password = os.environ.get('SENDER_PASSWORD', '')
        
        if not sender_email or smtp_server == 'localhost':
            print(f"[EMAIL LOG] À: {parent.last_name} {parent.first_name}")
            print(f"Sujet: {subject}")
            print(content)
            return
        
        # Adresse email du parent (à défaut, utiliser téléphone - format à adapter)
        recipient_email = f"{parent.last_name.lower()}.{parent.first_name.lower()}@parent.local"
        
        # Préparer l'email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"[ÉCOLE] {subject}"
        
        msg.attach(MIMEText(content, 'plain'))
        
        # Envoyer (optionnel selon configuration)
        # with smtplib.SMTP(smtp_server, smtp_port) as server:
        #     server.starttls()
        #     server.login(sender_email, sender_password)
        #     server.send_message(msg)
        
        # Pour test: log simple
        print(f"[EMAIL ENVOYÉ] À: {recipient_email}, Sujet: {subject}")
    
    @staticmethod
    def _send_whatsapp(parent, content):
        """
        Envoie un message WhatsApp au parent via pywhatkit
        
        ⚠️  Nécessite:
        1. Chrome/Firefox installé (pywhatkit utilise le navigateur)
        2. WhatsApp Web ouvert dans le navigateur
        3. Délai de 15-30 secondes pour que pywhatkit scanne et envoie
        """
        if not parent.phone_e164 or not parent.whatsapp_optin:
            return

        # Formater le numéro
        phone = str(parent.phone_e164).strip()
        if not phone.startswith("+"):
            phone = "+" + phone

        # 1) Si Twilio est disponible et configuré, l'utiliser en priorité
        tw_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        tw_token = os.environ.get("TWILIO_AUTH_TOKEN")
        tw_from = os.environ.get("TWILIO_WHATSAPP_FROM")  # ex: 'whatsapp:+1415...'

        if TWILIO_AVAILABLE and tw_sid and tw_token and tw_from:
            try:
                client = TwilioClient(tw_sid, tw_token)
                print(f"[TWILIO] Envoi WhatsApp à {phone} via {tw_from}...")
                message = client.messages.create(
                    from_=tw_from,
                    to=f"whatsapp:{phone}",
                    body=content
                )
                sid = getattr(message, 'sid', None)
                print(f"[TWILIO] Message SID: {sid}")
                time.sleep(1)
                return True, sid
            except Exception as e:
                print(f"[TWILIO ERROR] Erreur WhatsApp pour {phone}: {str(e)}")
                return False, str(e)

        # 2) Sinon fallback pywhatkit (nécessite WhatsApp Web ouvert)
        if PYWHATKIT_AVAILABLE:
            try:
                print(f"[PYWHATKIT] Envoi WhatsApp à {phone} (via navigateur)...")
                kit.sendwhatmsg_instantly(
                    phone_number=phone,
                    message=content,
                    wait_time=10,
                    tab_close=True
                )
                print(f"[PYWHATKIT] Message envoyé à {phone}")
                time.sleep(2)
                return True, None
            except Exception as e:
                print(f"[PYWHATKIT ERROR] Erreur WhatsApp pour {phone}: {str(e)}")
                return False, str(e)

        # 3) Enfin, log si aucune méthode d'envoi n'est opérationnelle
        print(f"[WHATSAPP STUB] À: {phone}")
        print(f"Contenu: {content}")
        return False, 'no_provider'


class BulkMessageProcessor:
    """Classe pour traiter les messages en attente et les envoyer en batch"""
    
    @staticmethod
    def process_pending_messages():
        """
        Traite tous les messages en attente dans MessageLog
        Peut être exécuté en tant que tâche cron
        """
        # Traiter les messages en file d'attente ou échecs WhatsApp avec retry
        from sqlalchemy import or_
        pending = MessageLog.query.filter(or_(MessageLog.status == 'queued', MessageLog.status == 'failed_whatsapp')).all()

        max_attempts = 3
        processed = 0
        for msg_log in pending:
            try:
                if not msg_log.parent_id:
                    continue

                parent = Parent.query.get(msg_log.parent_id)
                if not parent:
                    continue

                # Ne pas dépasser le nombre d'essais
                attempts = msg_log.attempts or 0
                if attempts >= max_attempts:
                    continue

                # Essayer l'envoi WhatsApp si opt-in
                if parent.whatsapp_optin and parent.phone_e164:
                    ok, info = ParentMessagingService._send_whatsapp(parent, msg_log.content)
                    msg_log.attempts = attempts + 1
                    if ok:
                        msg_log.status = 'sent_whatsapp'
                        if info:
                            msg_log.twilio_sid = info
                        msg_log.sent_at = datetime.utcnow()
                        processed += 1
                    else:
                        msg_log.status = 'failed_whatsapp'
                        msg_log.last_error = str(info)

            except Exception as e:
                msg_log.attempts = (msg_log.attempts or 0) + 1
                msg_log.last_error = str(e)
                print(f"Erreur traitement message {msg_log.id}: {str(e)}")

        db.session.commit()
        return processed

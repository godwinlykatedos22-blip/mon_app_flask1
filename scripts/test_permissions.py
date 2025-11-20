from app import create_app
from models import db, User, Student, Classe, Assessment

app = create_app()

with app.app_context():
    # Ensure a class and student exist
    classe = Classe.query.first()
    if not classe:
        classe = Classe(name='TestClass')
        db.session.add(classe)
        db.session.commit()

    student = Student.query.first()
    if not student:
        student = Student(first_name='Test', last_name='Student', class_id=classe.id)
        db.session.add(student)
        db.session.commit()

    # Create a test assessment to attempt deletion
    assessment = Assessment(student_id=student.id, subject='TestSubj', score=10, max_score=20, assessment_type='interrogation')
    db.session.add(assessment)
    db.session.commit()

    assessment_id = assessment.id

    client = app.test_client()

    def login_as(user):
        # Bypass CSRF/login form by injecting directly into session
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
        return client

    # Ensure test users exist (from test_roles)
    admin = User.query.filter_by(email='admin@test.local').first()
    director = User.query.filter_by(email='director@test.local').first()
    teacher = User.query.filter_by(email='teacher@test.local').first()

    if not admin or not director or not teacher:
        print('Les comptes de test manquent, exécute test_roles.py puis réessayez.')
        raise SystemExit(1)

    print('--- Test: accès suppression avec professeur (doit échouer) ---')
    login_as(teacher)
    # Vérifier d'abord le rendu du dashboard pour voir si les actions sont visibles
    res_dashboard = client.get('/notes/dashboard')
    dash_text = res_dashboard.get_data(as_text=True)
    print('Dashboard pour professeur contient bouton delete ?', 'btn-sm btn-danger' in dash_text)

    res = client.post(f'/notes/delete/{assessment_id}', follow_redirects=True)
    text = res.get_data(as_text=True)
    if 'Droits insuffisants' in text or 'Accès refusé' in text or 'Note supprim' not in text:
        print('✅ Professeur bloqué pour suppression (OK)')
    else:
        print('❌ Professeur a pu supprimer (PROBLÈME)')

    # Recreate assessment since delete might have happened
    if not Assessment.query.get(assessment_id):
        a = Assessment(student_id=student.id, subject='TestSubj', score=10, max_score=20, assessment_type='interrogation')
        db.session.add(a)
        db.session.commit()
        assessment_id = a.id

    print('--- Test: accès suppression avec directeur (doit réussir) ---')
    login_as(director)
    res_dashboard = client.get('/notes/dashboard')
    dash_text = res_dashboard.get_data(as_text=True)
    print('Dashboard pour directeur contient bouton delete ? ', 'btn-sm btn-danger' in dash_text)
    res = client.post(f'/notes/delete/{assessment_id}', follow_redirects=True)
    text = res.get_data(as_text=True)
    if 'Note supprim' in text:
        print('✅ Directeur a supprimé (OK)')
    else:
        print("❌ Directeur n'a pas pu supprimer (PROBLÈME)")
        print('--- Response begin ---')
        print(text)
        print('--- Response end ---')

    # Ensure admin can also delete (create new assessment)
    a2 = Assessment(student_id=student.id, subject='TestSubj2', score=12, max_score=20, assessment_type='devoir')
    db.session.add(a2)
    db.session.commit()
    aid2 = a2.id

    print('--- Test: accès suppression avec admin (doit réussir) ---')
    login_as(admin)
    res_dashboard = client.get('/notes/dashboard')
    dash_text = res_dashboard.get_data(as_text=True)
    print('Dashboard pour admin contient bouton delete ?     ', 'btn-sm btn-danger' in dash_text)
    res = client.post(f'/notes/delete/{aid2}', follow_redirects=True)
    text = res.get_data(as_text=True)
    if 'Note supprim' in text:
        print('✅ Admin a supprimé (OK)')
    else:
        print("❌ Admin n'a pas pu supprimer (PROBLÈME)")
        print('--- Response begin ---')
        print(text)
        print('--- Response end ---')

    print('\nTests permissions terminés.')

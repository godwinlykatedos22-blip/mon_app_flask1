from app import create_app
from models import db, User

app = create_app()

with app.app_context():
    client = app.test_client()

    def login_as(user):
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
        return client

    admin = User.query.filter_by(email='admin@test.local').first()
    director = User.query.filter_by(email='director@test.local').first()
    teacher = User.query.filter_by(email='teacher@test.local').first()

    if not admin or not director or not teacher:
        print('Manque comptes de test; exécute test_roles.py')
    else:
        for name, user in [('admin', admin), ('director', director), ('teacher', teacher)]:
            login_as(user)
            res = client.get('/notes/dashboard')
            text = res.get_data(as_text=True)
            has_delete = 'btn-sm btn-danger' in text
            has_edit = 'btn-sm btn-warning' in text
            has_user_name = (user.name or user.email) in text
            print(f"{name}: delete={has_delete} edit={has_edit} name_in_page={has_user_name} role={user.role}")

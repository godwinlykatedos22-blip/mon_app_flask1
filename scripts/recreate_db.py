from app import create_app
from models import db

app = create_app()
with app.app_context():
    print('Creating DB schema...')
    db.create_all()
    print('Done')

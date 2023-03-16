import os

from application.manage import create_app
from application.setup.db import db

# ===========# .=====================FILE TO CREATE TABLES IN DB================================================

if __name__ == '__main__':
    with create_app(os.getenv("FLASK_ENV", "development")).app_context():
        db.create_all()
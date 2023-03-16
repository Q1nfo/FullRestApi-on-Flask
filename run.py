import os

"""FILE TO CREATE APP AND BROWSE IT"""# .

from application.config import Config

from application.manage import create_app

app = create_app(Config())

app.run(host='0.0.0.0', port=8080)
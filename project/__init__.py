from flask import Flask

from flask_login import LoginManager
from project.models import db, User
from project.site import site
from project.api import api

app = Flask(__name__)

app.config.from_pyfile('../config.cfg', silent=False)

app.register_blueprint(site, url_prefix='')
app.register_blueprint(api, url_prefix='/api')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.blueprint_login_views = {
    'site': '/site/login'
}

db.app = app
db.init_app(app)
db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

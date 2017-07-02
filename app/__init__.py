import os

from flask import Flask, render_template
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

basedir = os.path.abspath(os.path.dirname(__name__))

mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'D\x94oc\x03QxY\xd8k\x81+\x83\x87k\x16]\xae\x12\xc0x\xf5Ma'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://gpacking:gpacking@localhost/gpacking'
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['GPACKING_MAIL_SUBJECT_PREFIX'] = '[GPacking]'
    app.config['GPACKING_MAIL_SENDER'] = 'GPacking Admin <gpacking@grouppacking.com>'
    #TODO: Create env variable
    app.config['GPACKING_ADMIN'] = 'admin@grouppacking.com'

    login_manager.init_app(app)
    mail.init_app(app)
    mail.init_app(app)
    db.init_app(app)

    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
import os


basedir = os.path.abspath(os.path.dirname(__name__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'D\x94oc\x03QxY\xd8k\x81+\x83\x87k\x16]\xae\x12\xc0x\xf5Ma'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager(app)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

login_manager.session_protection = 'strong'
login_manager.login_view = 'login'

from gpacking import views


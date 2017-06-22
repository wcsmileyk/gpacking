import os

from flask import Flask, render_template, url_for, redirect
from forms import LoginForm, CreateForm
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


basedir = os.path.abspath(os.path.dirname(__name__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'D\x94oc\x03QxY\xd8k\x81+\x83\x87k\x16]\xae\x12\xc0x\xf5Ma'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = form.email.data
        password = form.password.data
        return redirect('index')
    return render_template('login.html', form=form)


@app.route('/register')
def register():
    form = CreateForm()
    if form.validate_on_submit():
        fname = form.fname.data
        lname = form.lname.data
        email = form.email.data
        password = form.password.data
        confirm = form.confirm.data
        user = User(fname=fname, lname=lname, email=email, )
    return render_template('register.html')


@app.route('/logout')
def logout():
    return redirect('index')


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True)
    fname = db.Column(db.String(64))
    lname = db.Column(db.String(64))


    def __repr__(self):
        return '<User %r>' % self.name

    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


def create_user(fname, lname, )

if __name__ == "__main__":
    app.run(debug=True)


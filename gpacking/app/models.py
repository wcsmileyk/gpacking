from . import db, login_manager
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def create_roles():
        roles = {
            'User': (Permission.READ |
                     Permission.MANAGE, True),
            'Admin': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class AnonymousUser(AnonymousUserMixin):
    def allowed(self, permission):
        return False

    def is_admin(self):
        return False


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['GPACKING_ADMIN']:
                self.role = Role.qeury.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    confirmed = db.Column(db.Boolean, default=False)

    def confirm_token(self, expiration=3600):
        sig = Serializer(current_app.config['SECRET_KEY'], expiration)
        return sig.dumps({'confirm': self.id})

    def confirm(self, token):
        sig = Serializer(current_app.config['SECRET_KEY'])

        try:
            data = sig.loads(token)
        except:
            return False

        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def __repr__(self):
        return '<User %r>' % self.username


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def allowed(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_admin(self):
        return self.allowed(Permission.ADMIN)


class Permission:
    """
    User permission levels:

    READ: Can read inventory, and shared content
    MANAGE: Can manage inventory and shared content
    ADMIN: Site adminitration

    """
    READ = 0x01
    MANAGE = 0x02
    ADMIN = 0x08

login_manager.anonymous_user = AnonymousUser




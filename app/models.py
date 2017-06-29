from . import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime
from sqlalchemy.ext.associationproxy import association_proxy


inv_items = db.Table(
    'inv_items',
    db.Column('item_id', db.Integer, db.ForeignKey('items.id')),
    db.Column('inv_id', db.Integer, db.ForeignKey('inventories.id'))
)

group_assoc = db.Table(
    'groups_assoc',
    db.Column('inv_id', db.Integer, db.ForeignKey('inventories.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group_inventories.id'))
)

group_items = db.Table(
    'group_items',
    db.Column('group_id', db.Integer, db.ForeignKey('group_inventories.id')),
    db.Column('item_id', db.Integer, db.ForeignKey('items.id'))
)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class Friend(db.Model):
    __tablename__ = 'friends'
    """
    Status Codes:
    0 = pending
    1 = accepted
    2 = Blocked
    """

    requestor_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    requested_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    status = db.Column(db.Integer)
    action_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    __table_args__ = tuple(db.UniqueConstraint('requestor_id', 'requested_id', name='_friends_uc'))


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    inventories = db.relationship('Inventory', backref='user')

    confirmed = db.Column(db.Boolean, default=False)

    friends = db.relationship(
        'User',
        secondary='friends',
        primaryjoin=(Friend.requestor_id == id),
        secondaryjoin=(Friend.requested_id == id),
        lazy='dynamic'
    )

    def friendship_requested(self, user):
        if self.friends.filter_by(username=user.username).first() is not None \
                or Friend.query.filter_by(requestor_id=self.id).filter_by(requested_id=user.id).first() is not None:
            return True

    # def friend_status(self, user):
    #     friendship = self.friends.filter(User.id==user.id).first()
    #     if self.requested(user):
    #         if friendship.status == 0:
    #             return 'pending'
    #         elif friendship.status == 1:
    #             return 'accepted'
    #         elif friendship.status == 2:
    #             return 'blocked'
    #     else:
    #         return None
    #
    # def request_friend(self, user):
    #     if self.friend_status(user) is None:
    #         f = Friend(requestor_id=self.id, requested_id=user, status=0, action_user_id=user)
    #         db.session.add(f)
    #         db.session.commit()
    #
    # def requested(self, user):
    #     return self.friend_requestor.filter_by(requested_id=user.id).first() is not None
    #
    # def accept(self, user):
    #     friendship = self.friend_requested.filter_by(requestor_id=user.id).first()
    #     friendship.status = 1
    #     friendship.action_user_id = 0
    #     db.session.commit()
    #
    # def deny(self, user):
    #     friendship = self.friend_requested.filter_by(requestor_id=user.id).first()
    #     db.session.delete(friendship)
    #     db.session.commit()
    #
    # def block(self, user):
    #     if self.requested(user):
    #         self.friend_requestor.filter_by(requested_id=user.id).first().status = 2
    #     elif self.friend_requested.filter_by(requestor_id=user.id) is not None:
    #         self.friend_requested.filter_by(requestor_id=user.id).first().status = 2
    #     else:
    #         friendship = Friend(requestor_id=self.id, requested_id=user.id, action_user_id=0)
    #         db.session.add(friendship)
    #     db.session.commit()
    #
    # def remove_friend(self, user):
    #     if self.requested(user):
    #         friendship = self.friend_requestor.filter_by(requested_id=user.id).first()
    #     elif self.friend_requested.filter_by(requestor_id=user.id) is not None:
    #         friendship = self.friend_requested.filter_by(requestor_id=user.id).first()
    #     else:
    #         friendship = Friend(requestor_id=self.id, requested_id=user.id, action_user_id=0)
    #     db.session.delete(friendship)
    #     db.session.commit()

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

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(
                email=forgery_py.internet.email_address(),
                username=forgery_py.internet.user_name(),
                password=forgery_py.lorem_ipsum.word(),
                confirmed=True,
            )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    cat_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    type_id = db.Column(db.Integer, db.ForeignKey('types.id'))
    weight = db.Column(db.Integer)

    def __init__(self, name, cat_id, type_id, weight):
        self.name = name
        self.cat_id = cat_id
        self.type_id = type_id
        self.weight = weight


    def __repr__(self):
        return '<Item %r>' % self.name


class Activity(db.Model):
    __tablename__ = "activities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    inventories = db.relationship('Inventory', backref='activity', lazy='dynamic')

    def __repr__(self):
        return '<Activity %r>' % self.name


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    items = db.relationship('Item', backref='category', lazy='dynamic')
    types = db.relationship('Type', backref='category')

    def __repr__(self):
        return '<Category %r>' % self.name


class Type(db.Model):
    __tablename__ = "types"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    cat_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    items = db.relationship('Item', backref='type', lazy='dynamic')


    def __repr__(self):
        return '<Type %r>' % self.name


class Inventory(db.Model):
    __tablename__ = "inventories"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(128), index=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))
    primary = db.Column(db.Boolean)
    items = db.relationship('Item',
                            secondary=inv_items,
                            backref=db.backref('inventory', lazy='dynamic'),
                            lazy='dynamic'
                            )

    item_names = association_proxy('items', 'name')

    __table_args__ = tuple(db.UniqueConstraint('user_id', 'name', name='_user_invname_uc'))

    def __repr__(self):
        return '<Inventory %r>' % self.name

    @staticmethod
    def generate_fake(count=200):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            primary = True
            for inventory in u.inventories:
                if inventory.primary:
                    primary = False
            i = Inventory(
                name=forgery_py.lorem_ipsum.word(),
                user_id=u.id,
                primary=primary
            )
            db.session.add(i)
            db.session.commit()


class GroupInv(db.Model):
    __tablename__ = "group_inventories"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(64), index=True)
    ind_invs = db.relationship(
        'Inventory',
        secondary=group_assoc,
        backref=db.backref('group_inv', lazy='dynamic'),
        lazy='dynamic'
    )

    shared_items = db.relationship(
        'Item',
        secondary=group_items,
        backref=db.backref('group_inv', lazy='dynamic'),
        lazy='dynamic'
    )

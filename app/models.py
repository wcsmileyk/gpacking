from . import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime
from sqlalchemy.ext.associationproxy import association_proxy


closet_items = db.Table(
    'closet_items',
    db.Column('item_id', db.Integer, db.ForeignKey('items.id')),
    db.Column('closet_id', db.Integer, db.ForeignKey('closets.id'))
)

pl_items = db.Table(
    'pl_items',
    db.Column('item_id', db.Integer, db.ForeignKey('items.id')),
    db.Column('pl_id', db.Integer, db.ForeignKey('packing_lists.id'))
)

gl_items = db.Table(
    'gl_items',
    db.Column('item_id', db.Integer, db.ForeignKey('items.id')),
    db.Column('group_list_id', db.Integer, db.ForeignKey('group_lists.id'))
)

group_assoc = db.Table(
    'groups_assoc',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id'))
)

group_items = db.Table(
    'group_items',
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id')),
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
    status = db.Column(db.Integer, default=0)

    __table_args__ = tuple(db.UniqueConstraint('requestor_id', 'requested_id', name='_friends_uc'))

    def __repr__(self):
        return '<Friend: %r, %r>' % (User.query.get(self.requestor_id).username, User.query.get(self.requested_id).username)

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    closet = db.relationship('Closet', uselist=False, back_populates='user')
    packing_lists = db.relationship('PackingList', backref='user')
    group_lists = db.relationship('GroupList', backref='user')

    confirmed = db.Column(db.Boolean, default=False)

    friend_requested = db.relationship(
        'Friend',
        foreign_keys=[Friend.requestor_id],
        backref=db.backref('requestor', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    friend_requestor = db.relationship(
        'Friend',
        foreign_keys=[Friend.requested_id],
        backref=db.backref('requested', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

# User methods
    def my_friends(self):
        friends = []
        for friend in self.friend_requested.all():
            friends.append(User.query.get(friend.requested_id))
        for friend in self.friend_requestor.all():
            friends.append(User.query.get(friend.requestor_id))
        return friends

    def sent_request(self, user):
        return self.friend_requested.filter_by(requested_id=user.id).first() is not None

    def received_request(self, user):
        return self.friend_requestor.filter_by(requestor_id=user.id).first() is not None

    def friend_status(self, user):
        if self.sent_request(user):
            friendship = self.friend_requested.filter_by(requested_id=user.id).first()
            return friendship.status

    def request_friend(self, user):
        if self.friend_status(user) is None:
            f = Friend(requestor_id=self.id, requested_id=user.id, status=0)
            db.session.add(f)

    def accept(self, user):
        friendship = self.friend_requestor.filter_by(requestor_id=user.id).first()
        friendship.status = 1

    def deny(self, user):
        friendship = self.friend_requestor.filter_by(requestor_id=user.id).first()
        db.session.delete(friendship)

    def block(self, user):
        if self.sent_request(user):
            self.friend_requested.filter_by(requested_id=user.id).first().status = 2
        elif self.received_request(user):
            self.friend_requestor.filter_by(requestor_id=user.id).first().status = 2
        else:
            friendship = Friend(requestor_id=self.id, requested_id=user.id, status=2)
            db.session.add(friendship)

    def remove_friend(self, user):
        if self.sent_request(user):
            friendship = self.friend_requested.filter_by(requested_id=user.id).first()
        elif self.received_request(user):
            friendship = self.friend_requestor.filter_by(requestor_id=user.id).first()
        db.session.delete(friendship)

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
            closet = Closet(user_id=u.id)
            db.session.add(closet)
            u.closet = closet
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
    packing_lists = db.relationship('PackingList', backref='activity', lazy='dynamic')
    group_lists = db.relationship('Group', backref='activity', lazy='dynamic')

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


class Closet(db.Model):
    __tablename__ = "closets"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', uselist=False, back_populates='closet')
    items = db.relationship('Item',
                            secondary=closet_items,
                            backref=db.backref('closet', lazy='dynamic'),
                            lazy='dynamic'
                            )

    item_names = association_proxy('items', 'name')

    def __repr__(self):
        return '<Closet %r>' % self.id


class PackingList(db.Model):
    __tablename__ = "packing_lists"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(64), index=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    items = db.relationship('Item',
                            secondary=pl_items,
                            backref=db.backref('packing_list', lazy='dynamic'),
                            lazy='dynamic'
                            )

    item_names = association_proxy('items', 'name')

    def __repr__(self):
        return '<Packing List %r>' % self.name


class GroupList(db.Model):
    __tablename__ = "group_lists"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    items = db.relationship('Item',
                            secondary=gl_items,
                            backref=db.backref('group_lis', lazy='dynamic'),
                            lazy='dynamic'
                            )

    def __repr__(self):
        return '<Group List %r: %r>' % (Group.query.get(self.group_id).name, User.query.get(self.user_id).username)


class Group(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(64), index=True)
    users = db.relationship(
        'User',
        secondary=group_assoc,
        backref=db.backref('group', lazy='dynamic'),
        lazy='dynamic'
    )
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))

    shared_items = db.relationship(
        'Item',
        secondary=group_items,
        backref=db.backref('group', lazy='dynamic'),
        lazy='dynamic'
    )

    group_pls = db.relationship('GroupList', backref='group')

    def __repr__(self):
        return '<Group %r>' % self.name

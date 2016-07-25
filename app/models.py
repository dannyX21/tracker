from . import db
from datetime import datetime
from flask import current_app, request
from .email import send_email
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin, current_user
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from . import login_manager, db
import hashlib

class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('pos.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class PO_line(db.Model):
    __tablename__='pos'
    id = db.Column(db.Integer, primary_key=True)
    po_number = db.Column(db.String(16), unique=True)
    buyer = db.Column(db.String(2))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'))
    pn = db.Column(db.String(16))
    description = db.Column(db.String(64))
    po_date = db.Column(db.DateTime(), default=datetime.utcnow)
    qty_ordered = db.Column(db.Integer)
    qty_received = db.Column(db.Integer)
    balance = db.Column(db.Integer)
    expected_del_date = db.Column(db.DateTime(), default=None, nullable=True)
    ship_via_id = db.Column(db.Integer, db.ForeignKey('ship_vias.id'))
    tracking_number = db.Column(db.String(32), default=None, nullable=True)
    status = db.Column(db.Integer, default=0)
    priority = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, nullable=True)
    inv_type = db.Column(db.String(1), default="I")
    packing_slip_id = db.Column(db.Integer, db.ForeignKey('packing_slips.id'), nullable=True, default=None)
    coo_id = db.Column(db.Integer, db.ForeignKey('coos.id'), nullable=True, default=None)
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id], backref=db.backref('followed', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')
    posts = db.relationship('Post', backref='po_line', lazy='dynamic')

    @staticmethod
    def on_status_change(target, value, oldvalue, initiator):
        #print("PO# {}, Old Status: {}, New Status: {}.".format(target.po_number, oldvalue, value))
        print("oldvalue: {}, type: {}".format(oldvalue, type(oldvalue)))
        try:
            newstatus=current_app.config['STATUS_DICT'][value]
        except:
            newstatus=current_app.config['STATUS_DICT'][0]
        try:
            oldstatus=current_app.config['STATUS_DICT'][oldvalue]
        except:
            oldstatus=current_app.config['STATUS_DICT'][0]
        for follower in target.followers:
            user = User.query.get_or_404(follower.follower_id)
            send_email(user.email, 'PO# %s Status Update' % target.po_number, 'status_update', po_line=target, oldstatus=oldstatus, newstatus=newstatus)

    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.follower_id).first() is not None

class Vendor(db.Model):
    __tablename__ = 'vendors'
    id = db.Column(db.Integer, primary_key=True)
    vendor_number = db.Column(db.Integer, unique=True)
    name = db.Column(db.String(64))
    contact = db.Column(db.String(32), nullable=True, default=None)
    email = db.Column(db.String(64), nullable=True, default=None)
    website = db.Column(db.String(64), nullable=True, default=None)
    phone = db.Column(db.String(16), nullable=True, default=None)
    po_lines = db.relationship('PO_line', backref='vendor', lazy='dynamic')
    default_ship_via_id = db.Column(db.Integer, db.ForeignKey('ship_vias.id'))

class Ship_via(db.Model):
    __tablename__ = 'ship_vias'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(4), unique=True, nullable=False)
    name = db.Column(db.String(32), nullable=False)
    tracking_url = db.Column(db.String(64), default=None, nullable=True)
    po_lines = db.relationship('PO_line', backref='ship_via', lazy='dynamic')
    default_ship_via = db.relationship('Vendor', backref='default_ship_via', lazy='dynamic')

class Packing_slip(db.Model):
    __tablename__ ='packing_slips'
    id = db.Column(db.Integer, primary_key=True)
    delivery_date = db.Column(db.DateTime(),default=datetime.utcnow)
    notes = db.Column(db.String(128), default=None, nullable=True)
    po_lines = db.relationship('PO_line',backref='packing_slip', lazy='dynamic')

class Coo(db.Model):
    __tablename__ ='coos'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'))
    effective_since = db.Column(db.DateTime(),default=datetime.utcnow)
    effective_until = db.Column(db.DateTime(), default=None, nullable=True)
    valid = db.Column(db.Boolean)
    po_lines = db.relationship('PO_line',backref='coo', lazy='dynamic')

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
        'User': (Permission.VIEW | Permission.COMMENT | Permission.SUBSCRIBE, True),
        'Operator': (Permission.VIEW | Permission.COMMENT | Permission.SUBSCRIBE | Permission.MODIFY, False),
        'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64),unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64))
    position = db.Column(db.String(64))
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    avatar_hash = db.Column(db.String(32))
    followed = db.relationship('Follow',foreign_keys=[Follow.follower_id],backref=db.backref('follower', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='retro', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default, rating=rating)

    def follow(self,po_line):
        if not self.is_following(po_line):
            f = Follow(follower=self, followed=po_line)
            db.session.add(f)
            db.session.commit()

    def unfollow(self,po_line):
        f = self.followed.filter_by(followed_id=po_line.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    def is_following(self, po_line):
        return self.followed.filter_by(followed_id=po_line.id).first() is not None

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['TRACKER_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()


    def __repr__(self):
        return '<User %r>' % self.username

class Post(db.Model):
    __tablename__='posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id =db.Column(db.Integer, db.ForeignKey('users.id'))
    po_line_id = db.Column(db.Integer, db.ForeignKey('pos.id'))

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

class Permission:
    VIEW = 0x01
    COMMENT = 0x02
    SUBSCRIBE = 0x04
    MODIFY = 0x08
    ADMINISTER = 0x80

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

login_manager.anonymous_user = AnonymousUser

db.event.listen(PO_line.status, 'set', PO_line.on_status_change)

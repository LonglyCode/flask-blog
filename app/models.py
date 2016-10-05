# -*- coding: utf-8 -*-

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask.ext.login import UserMixin, AnonymousUserMixin
from . import db, login_manager
from datetime import datetime
from jinja2.filters import do_striptags, do_truncate
from .utils import markdown_render

class Todo(db.Model):
    __tablename__="testtodos"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(128))
    time =db.Column(db.DateTime,default=datetime.now())
    status = db.Column(db.Integer,default=0)

    def to_json(self):
        return {
            'id':self.id,
            'content':self.content,
            'time':self.time,
            'status':self.status
        }

class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


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
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
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
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post',backref='author',lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['APP_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
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

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


post_tags_table = db.Table(
    'post_tags',
    db.Model.metadata,
    db.Column('post_id', db.Integer, db.ForeignKey(
        "posts.id", ondelete='CASCADE')),
    db.Column('tag_id', db.Integer, db.ForeignKey(
        "tags.id", ondelete='CASCADE')),
)

class Tag(db.Model):
    __tablename__="tags"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True,nullable=False)
    name_html = db.Column(db.Text)
    __mapper_args__ = {'order_by': [id.desc()]}

    def __repr__(self):
        return '<Tag %r>' % (self.name)

    @staticmethod
    def on_chang_body(target,value,oldvalue,initiator):
        target.name_html = markdown_render(value,codehilite=True)

db.event.listen(Tag.name, 'set', Tag.on_chang_body)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(200),nullable=False)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    pub_time = db.Column(db.DateTime,index=True,default=datetime.now)
    summary = db.Column(db.String(2000))
    modified_time = db.Column(db.DateTime, default=datetime.now)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    category_id =db.Column(db.Integer,db.ForeignKey('categorys.id'))

    tags = db.relationship(
        Tag, secondary=post_tags_table, backref=db.backref("posts"))


    def __repr__(self):
        return '<post %r>' % (self.title)

    @staticmethod
    def on_chang_body(target,value,oldvalue,initiator):
        target.body_html = markdown_render(value,codehilite=True)

    @staticmethod
    def insert_summary(mapper,connection,target):
        def _format(_html):
            return do_truncate(do_striptags(_html), length=200)
        value = target.body
        if target.summary is None or target.summary.strip() == '':
            target.summary = _format(value)

db.event.listen(Post.body,'set',Post.on_chang_body)
db.event.listen(Post,'before_insert',Post.insert_summary)


class Category(db.Model):
    __tablename__="categorys"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30),nullable=False)
    name_html = db.Column(db.Text)
    posts = db.relationship('Post',backref='category',lazy='dynamic')

    def __repr__(self):
        return '<Category %r>' % (self.name)

    @staticmethod
    def on_chang_body(target,value,oldvalue,initiator):
        target.name_html = markdown_render(value,codehilite=True)

db.event.listen(Category.name, 'set', Category.on_chang_body)

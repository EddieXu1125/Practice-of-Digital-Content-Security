from flask import Flask
from flask.globals import current_app
from flask_login.mixins import AnonymousUserMixin
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context
from ext import db
from config import BaseConfig
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
from flask_login import UserMixin, login_manager
from datetime import datetime

class Users(db.Model,UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(150))
    email = db.Column(db.String(100))
    brief = db.Column(db.String(200))

    #photos = db.relationship('Photo', back_populates='author', cascade='all')
   
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

    def hash_password(self, password):
        self.password = custom_app_context.encrypt(password)
    
    def verify_password(self, password):
        return custom_app_context.verify(password, self.password)
 
    def generate_auth_token(self, expiration = 600):
        s = Serializer(BaseConfig.SECRET_KEY, expires_in = expiration)
        return s.dumps({ 'id': self.id })

    def verify_token(token):
        s = Serializer(BaseConfig.SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        user = Users.query.get(data['id'])
        return user

    def is_authenticated(self):
        return True
 
    def is_active(self):
        return True
 
    def is_anonymous(self):
        return False

    def to_json(self):
        dict = self.__dict__
        print(type(dict))
        if "_sa_instance_state" in dict.keys():
            dict.pop('_sa_instance_state')
        return dict

class Photo(db.Model):
    __tablename__ = 'photo'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(500))
    filename = db.Column(db.String(1000)) 
    filepath = db.Column(db.String(10000))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    #author = db.relationship('Users', back_populates='photos')
    # comments = db.relationship('Comment', back_populates='photo', cascade='all')
    # collectors = db.relationship('Collect', back_populates='collected', cascade='all')

    def __init__(self, filename, filepath,author_id):
        self.filename = filename
        self.filepath = filepath
        self.author_id = author_id
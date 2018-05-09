from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

participants = db.Table(
    'participants',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('dinner_id', db.Integer, db.ForeignKey('dinner.id'))
)

chefs = db.Table(
    'chefs',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('dinner_id', db.Integer, db.ForeignKey('dinner.id'))
)

items = db.Table(
    'items',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('shopping_id', db.Integer, db.ForeignKey('shopping.id')),
)

drinks = db.Table(
    'drinks',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('beverage_club.id', db.Integer, db.ForeignKey('user.id')),
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String(50), unique=True)
    admin = db.Column(db.Boolean)
    subscribed_to_dinner_club = db.Column(db.Boolean, nullable=False)


class Dinner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payee = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Float, nullable=False)
    participants = db.relationship('User', secondary=participants, backref=db.backref('participants', lazy='dynamic'))
    chefs = db.relationship('User', secondary=chefs, backref=db.backref('chefs', lazy='dynamic'))


class Shopping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payee = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    items = db.relationship('User', secondary=items, backref=db.backref('items', lazy='dynamic'))


class BeverageClub(db.Model):
    __table_name__ = 'beverage_club'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    drinks = db.relationship('User', secondary=drinks, backref=db.backref('drinks', lazy='dynamic'))

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

participants = db.Table(
    'participants',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('dinner_id', db.Integer, db.ForeignKey('dinner.id'))
)

guests = db.Table(
    'guests',
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
    db.Column('beverage_club.id', db.Integer, db.ForeignKey('beverage_club.id')),
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True, nullable=False)
    room_number = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String, nullable=False)
    admin = db.Column(db.Boolean, default=False)
    subscribed_to_dinner_club = db.Column(db.Boolean)
    move_in_date = db.Column(db.Date, default=date.today(), nullable=False)
    move_out_date = db.Column(db.Date)
    phone_number = db.Column(db.String)
    active = db.Column(db.Boolean)
    dinner_balance = db.Column(db.Float, default=0)
    picture_url = db.Column(db.String())
    dinners_paid = db.relationship('Dinner', backref='payee', lazy=True)


class Dinner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    participants = db.relationship('User', secondary=participants, backref=db.backref('dinners', lazy='dynamic'))
    guests = db.relationship('User', secondary=guests, backref=db.backref('dinner_guests', lazy='dynamic'))
    chefs = db.relationship('User', secondary=chefs, backref=db.backref('dinners_where_cooked', lazy='dynamic'))
    dish_name = db.Column(db.String)
    accounted = db.Column(db.Boolean, default=False)


class Shopping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payee = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    items = db.relationship('User', secondary=items, backref=db.backref('bought_items', lazy='dynamic'))


class BeverageClub(db.Model):
    __table_name__ = 'beverage_club'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    drinks = db.relationship('User', secondary=drinks, backref=db.backref('drinks_consumed', lazy='dynamic'))

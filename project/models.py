from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin
from datetime import date, datetime

db = SQLAlchemy()

participants = db.Table(
    "participants",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("dinner_id", db.Integer, db.ForeignKey("dinner.id"))
)

chefs = db.Table(
    "chefs",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("dinner_id", db.Integer, db.ForeignKey("dinner.id"))
)

drinks = db.Table(
    "drinks",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("beverage_club_id", db.Integer, db.ForeignKey("beverage_club.id")),
)


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True, nullable=False)
    room_number = db.Column(db.Integer, default=0, nullable=False)
    admin = db.Column(db.Boolean, default=False)
    subscribed_to_dinner_club = db.Column(db.Boolean)
    move_in_date = db.Column(db.Date, default=date.today(), nullable=False)
    move_out_date = db.Column(db.Date)
    phone_number = db.Column(db.String)
    active = db.Column(db.Boolean)
    picture_url = db.Column(db.String)
    dinners_paid = db.relationship("Dinner", backref="payee", lazy=True)
    guests = db.relationship("GuestAssociation", back_populates="user")
    meeting_topics = db.relationship("MeetingTopic", backref="user", lazy=True)
    items = db.relationship("Items", back_populates="user")


class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)
    provider_user_id = db.Column(db.String(255), unique=True)


class Dinner(db.Model):
    __tablename__ = 'dinner'
    id = db.Column(db.Integer, primary_key=True)
    payee_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    participants = db.relationship("User", secondary=participants, backref=db.backref("dinners", lazy="dynamic"))
    guests = db.relationship("GuestAssociation", back_populates="dinner")
    chefs = db.relationship("User", secondary=chefs, backref=db.backref("dinners_where_cooked", lazy="dynamic"))
    dish_name = db.Column(db.String)
    accounted = db.Column(db.Boolean, default=False)


class GuestAssociation(db.Model):
    __tablename__ = 'guest_association'
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key=True)
    dinner_id = db.Column(db.Integer, db.ForeignKey(Dinner.id), primary_key=True)
    number_of_guests = db.Column(db.Integer, nullable=False)
    user = db.relationship("User", back_populates="guests")
    dinner = db.relationship("Dinner", back_populates="guests")


class Shopping(db.Model):
    __tablename__ = 'shopping'
    id = db.Column(db.Integer, primary_key=True)
    payee_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    payee = db.relationship(User)
    date = db.Column(db.Date, nullable=False)
    items = db.relationship("Items", back_populates="shopping")
    accounted = db.Column(db.Boolean, default=False)


class Items(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    shopping_id = db.Column(db.Integer, db.ForeignKey("shopping.id"))
    price = db.Column(db.Float, nullable=False)
    name = db.Column(db.String, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    user = db.relationship(User, back_populates="items")
    shopping = db.relationship(Shopping, back_populates="items")


class BeverageClub(db.Model):
    __table_name__ = "beverage_club"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    drinks = db.relationship(User, secondary=drinks, backref=db.backref("drinks_consumed", lazy="dynamic"))


class MeetingEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, default=False)


class MeetingTopic(db.Model):
    __table_name__ = "kitchen_meeting_topic"
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    talked_about = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    meeting_id = db.Column(db.Integer, db.ForeignKey(MeetingEvent.id))

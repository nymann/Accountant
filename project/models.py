from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin
from datetime import datetime
import enum

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


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String)
    room_number = db.Column(db.Integer)
    admin = db.Column(db.Boolean, default=False)
    subscribed_to_dinner_club = db.Column(db.Boolean)
    move_in_date = db.Column(db.Date, default=datetime.strptime("01/01/2000", "%m/%d/%Y"), nullable=False)
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
    provider_user_id = db.Column(db.String(255), unique=True, nullable=False)


class Dinner(db.Model):
    __tablename__ = 'dinner'
    id = db.Column(db.Integer, primary_key=True)
    payee_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    price = db.Column(db.Float, default=0.0)
    datetime = db.Column(db.DateTime, nullable=False)
    participants = db.relationship("User", secondary=participants, backref=db.backref("dinners", lazy="dynamic"))
    guests = db.relationship("GuestAssociation", back_populates="dinner")
    chefs = db.relationship("User", secondary=chefs, backref=db.backref("dinners_where_cooked", lazy="dynamic"))
    dish_name = db.Column(db.String)
    picture_url = db.Column(db.String)
    accounting_id = db.Column(db.ForeignKey("accounting_report.id"), nullable=True)


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
    accounting_id = db.Column(db.ForeignKey("accounting_report.id"), nullable=True)


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


class NeededItems(db.Model):
    __tablename__ = 'needed_items'
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String, nullable=False)
    item_bought = db.Column(db.Boolean, default=False)


class MeetingEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, default=False)


class MeetingTopic(db.Model):
    __tablename__ = "kitchen_meeting_topic"
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    date = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    talked_about = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    meeting_id = db.Column(db.Integer, db.ForeignKey(MeetingEvent.id))


class BeverageTypes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=False)


class Beverage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    contents = db.Column(db.Float, nullable=False)
    type = db.Column(db.String, db.ForeignKey(BeverageTypes.id))


class BeverageBatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    beverage_id = db.Column(db.Integer, db.ForeignKey(Beverage.id))
    quantity = db.Column(db.Integer, nullable=False)
    price_per_can = db.Column(db.Float, nullable=False)
    payee_id = db.Column(db.ForeignKey(User.id), nullable=False)
    accounting_id = db.Column(db.ForeignKey("accounting_report.id"), nullable=True)


class BeverageID(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    beverage_id = db.Column(db.Integer, db.ForeignKey(Beverage.id))


class BeverageUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    beverage_batch_id = db.Column(db.Integer, db.ForeignKey(BeverageBatch.id))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    timestamp = db.Column(db.DateTime, default=datetime.now(), nullable=False)


class UserReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship(User)
    paid = db.Column(db.Boolean, default=False, nullable=False)
    dinner_balance = db.Column(db.Float, nullable=False)
    shopping_balance = db.Column(db.Float, nullable=False)
    beverage_balance = db.Column(db.Float, nullable=False)
    total_balance = db.Column(db.Float, nullable=False)
    accounting_report_id = db.Column(db.Integer, db.ForeignKey("accounting_report.id"))


class AccountingReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_reports = db.relationship("UserReport")
    date = db.Column(db.DateTime, default=datetime.now(), nullable=False)


class FeedbackLabel(enum.Enum):
    BUG = "Bug"
    IMPROVEMENT = "Improvement"
    FEATURE = "New Feature"
    QUESTION = "Question"
    OTHER = "Other"


class FeedbackStatus(enum.Enum):
    NEW = "New"
    STARTED = "In progress"
    CLOSED = "Closed"


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    header = db.Column(db.String, nullable=False)
    author = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    status = db.Column(db.Enum(FeedbackStatus), default=FeedbackStatus.NEW)
    label = db.Column(db.Enum(FeedbackLabel), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(), nullable=False)


class FeedbackComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feedback_id = db.Column(db.Integer, db.ForeignKey(Feedback.id), nullable=False)
    author = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    comment = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(), nullable=False)


class FeedbackPicture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feedback_comment_id = db.Column(db.Integer, db.ForeignKey(FeedbackComment.id), nullable=False)
    picture_url = db.Column(db.String)

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, FileField, SelectMultipleField, SelectField
from wtforms.validators import InputRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    # Max length of passwords are 80, because of sha256 generates a 80 char. long password.
    email = StringField('email')
    password = PasswordField('password')
    remember = BooleanField('remember')


class RegisterForm(FlaskForm):
    name = StringField('name')
    email = StringField('email')
    password = PasswordField('password')
    password_again = PasswordField('password_again')
    room_number = StringField('room_number')


class UserForm(FlaskForm):
    name = StringField('name')
    email = StringField('email')
    admin = BooleanField('admin')
    subscribed_to_dinner_club = BooleanField('subscribed_to_dinner_club')
    room_number = StringField('room_number')
    phone_number = StringField('phone_number')
    active = BooleanField('active')
    picture = FileField('picture')
    move_in_date = StringField('move_in_date')
    move_out_date = StringField('move_out_date')


class DinnerForm(FlaskForm):
    price = StringField('price')
    date = StringField('date')
    guests = StringField('guests')
    dish_name = StringField('dish_name')
    payee = StringField('payee')


class MeetingTopicForm(FlaskForm):
    topic = StringField('topic')
    description = StringField('description')


class MeetingEventForm(FlaskForm):
    date = StringField('date')


class ShoppingForm(FlaskForm):
    date = StringField('date')
    payee = StringField('payee')


class ItemForm(FlaskForm):
    name = StringField('name')
    amount = StringField('amount')
    price = StringField('price')


class NewBeverageForm(FlaskForm):
    name = StringField('name')
    type = StringField('type')
    contents = StringField('content')


class NewBeverageBatchForm(FlaskForm):
    beverage_id = StringField('beverage_id')
    quantity = StringField('quantity')
    price = StringField('price')


class BuyBeverageForm(FlaskForm):
    beverage_id = StringField('beverage_id')

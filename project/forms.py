from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    # Max length of passwords are 80, because of sha256 generates a 80 char. long password.
    email = StringField('email')
    password = PasswordField('password')
    remember = BooleanField('remember')


class RegisterForm(FlaskForm):
    email = StringField('email')
    password = PasswordField('password')
    password_again = PasswordField('password_again')


class UserForm(FlaskForm):
    name = StringField('name')
    email = StringField('name')
    admin = BooleanField('admin')
    subscribed_to_dinner_club = BooleanField('subscribed_to_dinner_club')

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, FileField, SelectMultipleField, SelectField
from wtforms.validators import InputRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    # Max length of passwords are 80, because of sha256 generates a 80 char. long password.
    email = StringField('email')
    password = PasswordField('password')
    remember = BooleanField('remember')


class RegisterForm(LoginForm):
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
    time = StringField('time')


class DinnerEntriesForm(FlaskForm):
    dates = StringField('dates')
    time = StringField('time')


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


class NeededItemForm(FlaskForm):
    item_name = StringField('item_name')


class NewBeverageForm(FlaskForm):
    name = StringField('name')
    type = StringField('type')
    contents = StringField('content')


class NewBeverageBatchForm(FlaskForm):
    beverage_id = StringField('beverage_id')
    quantity = StringField('quantity')
    price = StringField('price')
    payee_id = StringField('payee_id')


class BuyBeverageForm(FlaskForm):
    beverage_id = StringField('beverage_id')


class NewBeverageTypesForm(FlaskForm):
    type_new = StringField('type_new')


class ParticipateForm(FlaskForm):
    dinner_id = StringField('dinner_id')


class BuyBeverageAdminForm(FlaskForm):
    beverage_id = StringField('beverage_id')
    user_id = StringField('user_id')
    amount = StringField('amount')


class FeedbackForm(FlaskForm):
    feedback_header = StringField('feedback_header')
    feedback_description = StringField('feedback_description')
    feedback_label = StringField('feedback_label')


class FeedbackCommentForm(FlaskForm):
    feedback_comment = StringField('feedback_comment')

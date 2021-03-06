from datetime import datetime

from flask_login import current_user
from sqlalchemy import func, or_

from project.models import db, Shopping, User, Items, Dinner, BeverageBatch, BeverageUser, UserReport

from ics import Calendar, Event

import arrow


def is_admin():
    return current_user.is_authenticated and current_user.admin


def is_active():
    return current_user.is_authenticated and current_user.active


def generate_calendar():
    # Getting Dinners
    dinners = Dinner.query.filter(
        Dinner.accounting_id.is_(None)
    ).all()
    #
    calender = Calendar()
    for dinner in dinners:
        event = Event()
        event.name = "Madklub - " + dinner.dish_name
        time = arrow.get(dinner.madtid, '+02:00')
        event.begin = time
        # event.location("55.810817, 12.515183")

        # participant_list = ''
        # for participant in dinner.participants:
        #     participant_list+= participant + '\n'
        # event.description(participant_list)
        # event.url('https://kk24.dk/dinner_club/meal/'+str(dinner.id))
        # event.duration({"hours":1})

        calender.events.add(event)

    # calender.events
    # with open('project/static/calendar/calendar.ics', 'w') as calender_file:
    #     calender_file.writelines(calender)


def send_accounting_mail(account_id):
    report_users = UserReport.query.filter(
        UserReport.accounting_report_id.is_(account_id)
    ).all()

    users = []
    for report_user in report_users:
        user = User.query.filter(User.id.is_(report_user.user_id)).first()
        if '@' in user.email:
            users.append(user)

    for user in users:

        user_report = UserReport.query.filter(
            UserReport.accounting_report_id.is_(account_id),
            UserReport.user_id.is_(user.id)
        ).first()
        name = user.name
        user_email = user.email
        dinner = round(user_report.dinner_balance, 2)
        shopping = round(user_report.shopping_balance, 2)
        beverage = round(user_report.beverage_balance, 2)
        total = round(user_report.total_balance, 2)

        msg = """
                   <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
    <title>KK24.dk</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=250px, initial-scale=1.0 " />
    <meta charset="UTF-8">

</head>


<body>
    <center>
        <h1>Hi {}</h1>
        <h3>The accounts have been made, you can now pay your share!</h3>
        <h3>Below you can see an overview of your share.<br> More information can be viewed on the web page.<br><a href="https://kk24.dk/reports">kk24.dk</a></h3></h3>
        <br>
        <br>
        <table>
            <tr>
                <td>Dinner club balance:</td>
                <td>{}</td>
            </tr>
            <tr>
                <td>Shopping balance:</td>
                <td>{}</td>
            </tr>
            <tr>
                <td>Beverage balance:</td>
                <td>{}</td>
            </tr>
            <tr>
                <td></td>
                <td></td>
            </tr>
            <tr>
                <td>Total:</td>
                <td>{}</td>
            </tr>
        </table>
        <br>
        <br>
        <br>        
        <h3>Best regards Accountant</h3>
    </center>
</body>

</html>
                        
        """.format(name, dinner, shopping, beverage, total)

        from send_email import send_an_email
        send_an_email([user_email], msg, 'Accountant | kk24.dk')


class UserHelper:
    def __init__(self, user):
        self.user = user

    def shopping_income(self, accounting_id=None):
        shopping_income = db.session.query(
            func.sum(Items.price * Items.amount)
        ).join(Shopping).filter(
            Shopping.accounting_id.is_(accounting_id),
            Shopping.payee_id.is_(self.user.id),
        ).scalar()
        return shopping_income if shopping_income else 0.0

    def shopping_expenses(self, accounting_id=None):
        shopping_entries = Shopping.query.filter(
            Shopping.accounting_id.is_(accounting_id)
        ).all()

        shopping_expenses = 0.0
        if self.user.active:
            for shopping in shopping_entries:
                active_members = db.session.query(
                    func.count(User.id)
                ).filter(
                    User.active,
                    or_(User.move_out_date.is_(None), User.move_out_date >= shopping.date),
                    or_(User.move_in_date.is_(None), User.move_in_date <= shopping.date)
                ).scalar()
                for item in shopping.items:
                    if (self.user.move_in_date is None or self.user.move_in_date <= shopping.date) and (
                            self.user.move_out_date is None or self.user.move_out_date >= shopping.date):
                        shopping_expenses += (item.price * item.amount) / active_members
        return shopping_expenses

    def shopping_balance(self, accounting_id=None):
        return self.shopping_income(accounting_id) - self.shopping_expenses(accounting_id)

    def dinner_income(self, accounting_id=None):
        dinner_income = db.session.query(
            func.sum(Dinner.price)
        ).filter(
            Dinner.payee_id.is_(self.user.id),
            Dinner.accounting_id.is_(accounting_id),
            Dinner.madtid < datetime.now()
        ).scalar()
        return dinner_income if dinner_income else 0.0

    def dinner_expenses(self, accounting_id=None):
        dinners = Dinner.query.filter(
            Dinner.accounting_id.is_(accounting_id),
            Dinner.madtid < datetime.now()
        ).all()
        dinner_expenses = 0.0
        if self.user.active:
            for dinner in dinners:
                if self.user not in dinner.participants:
                    continue
                # How many participated?
                number_of_guests = 0
                for guest in dinner.guests:
                    number_of_guests += guest.number_of_guests
                number_of_participants = len(dinner.participants) + number_of_guests
                dinner_expenses += dinner.price / number_of_participants
                for guest in dinner.guests:
                    if guest.user_id is self.user.id:
                        # It's our guest.
                        dinner_expenses += guest.number_of_guests * dinner.price / number_of_participants
        return dinner_expenses

    def dinner_balance(self, accounting_id=None):
        return self.dinner_income(accounting_id) - self.dinner_expenses(accounting_id)

    def beverage_income(self, accounting_id=None):
        beverage_income = db.session.query(
            func.sum(BeverageBatch.price_per_can)
        ).join(BeverageUser).filter(
            BeverageBatch.payee_id == self.user.id,
            BeverageUser.accounting_id.is_(accounting_id)
        ).scalar()
        return beverage_income if beverage_income else 0.0

    def beverage_expenses(self, accounting_id=None):
        beverage_expenses = db.session.query(
            func.sum(BeverageBatch.price_per_can)
        ).join(
            BeverageUser
        ).filter(
            BeverageUser.user_id == self.user.id,
            BeverageUser.accounting_id.is_(accounting_id)
        ).scalar()
        return beverage_expenses if beverage_expenses else 0.0

    def beverage_balance(self, accounting_id=None):
        return self.beverage_income(accounting_id) - self.beverage_expenses(accounting_id)

    def total_expenses(self, accounting_id=None):
        return self.shopping_expenses(accounting_id) + self.dinner_expenses(accounting_id) + self.beverage_expenses(
            accounting_id)

    def total_income(self, accounting_id=None):
        return self.shopping_income(accounting_id) + self.dinner_income(accounting_id) + self.beverage_income(
            accounting_id)

    def total_balance(self, accounting_id=None):
        return self.total_income(accounting_id) - self.total_expenses(accounting_id)

    @staticmethod
    def active_members(shopping):
        active_members = db.session.query(
            func.count(User.id)
        ).filter(
            User.active,
            or_(User.move_out_date.is_(None), User.move_out_date >= shopping.date),
            or_(User.move_in_date.is_(None), User.move_in_date <= shopping.date)
        ).scalar()
        return active_members

    def shopping_entry_effect_on_balance(self, shopping):
        active_members = self.active_members(shopping)
        shopping_entry_price_total = 0
        for item in shopping.items:
            shopping_entry_price_total += item.price * item.amount
        if shopping.payee_id == self.user.id:
            return shopping_entry_price_total - (shopping_entry_price_total / active_members)
        else:
            return -(shopping_entry_price_total / active_members)

    def __str__(self, accounting_id=None):
        return "_________________________\n" \
               "%s:\n" % self.user.name + \
               "total income: {0}\n" \
               "\tdinner {1} DKK\n" \
               "\tshopping {2} DKK\n" \
               "\tbeverage {3} DKK\n" \
               "total expenses {4} DKK\n" \
               "\tdinner {5} DKK\n" \
               "\tshopping {6} DKK\n" \
               "\tbeverage {7} DKK\n" \
               "TOTAL BALANCE: {8} DKK".format(
                   self.total_income(accounting_id),
                   self.dinner_income(accounting_id),
                   self.shopping_income(accounting_id),
                   self.beverage_income(accounting_id),
                   self.total_expenses(accounting_id),
                   self.dinner_expenses(accounting_id),
                   self.shopping_expenses(accounting_id),
                   self.beverage_expenses(accounting_id),
                   self.total_balance(accounting_id)
               )

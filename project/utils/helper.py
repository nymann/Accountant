from datetime import datetime

from flask_login import current_user
from sqlalchemy import func, or_

from project.models import db, Shopping, User, Items, Dinner, BeverageBatch, BeverageUser


def is_admin():
    return current_user.is_authenticated and current_user.admin


def is_active():
    return current_user.is_authenticated and current_user.active


class UserHelper:
    def __init__(self, user):
        self.user = user

    def shopping_income(self):
        shopping_income = db.session.query(
            func.sum(Items.price * Items.amount)
        ).join(Shopping).filter(
            Shopping.accounted.is_(False),
            Shopping.payee_id.is_(self.user.id),
        ).scalar()
        return shopping_income if shopping_income else 0.0

    def shopping_expenses(self):
        non_accounted_shopping_entries = Shopping.query.filter(
            Shopping.accounted.is_(False)
        ).all()

        shopping_expenses = 0.0
        if self.user.active:
            for shopping in non_accounted_shopping_entries:
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

    def shopping_balance(self):
        return self.shopping_income() - self.shopping_expenses()

    def dinner_income(self):
        dinner_income = db.session.query(
            func.sum(Dinner.price)
        ).filter(
            Dinner.payee_id.is_(self.user.id),
            Dinner.accounted.is_(False),
            Dinner.datetime < datetime.now()
        ).scalar()
        return dinner_income if dinner_income else 0.0

    def dinner_expenses(self):
        non_accounted_dinners = Dinner.query.filter(
            Dinner.accounted.is_(False),
            Dinner.datetime < datetime.now()
        ).all()
        dinner_expenses = 0.0
        if self.user.active:
            for dinner in non_accounted_dinners:
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

    def dinner_balance(self):
        return self.dinner_income() - self.dinner_expenses()

    def beverage_income(self):
        beverage_income = db.session.query(
            func.sum(BeverageBatch.price_per_can)
        ).join(BeverageUser).filter(
            BeverageBatch.payee_id == self.user.id,
            BeverageBatch.accounted.is_(False)
        ).scalar()
        return beverage_income if beverage_income else 0.0

    def beverage_expenses(self):
        beverage_expenses = db.session.query(
            func.sum(BeverageBatch.price_per_can)
        ).join(
            BeverageUser
        ).filter(
            BeverageUser.user_id == self.user.id,
            BeverageBatch.accounted.is_(False)
        ).scalar()
        return beverage_expenses if beverage_expenses else 0.0

    def beverage_balance(self):
        return self.beverage_income() - self.beverage_expenses()

    def total_expenses(self):
        return self.shopping_expenses() + self.dinner_expenses() + self.beverage_expenses()

    def total_income(self):
        return self.shopping_income() + self.dinner_income() + self.beverage_income()

    def total_balance(self):
        return self.total_income() - self.total_expenses()

    def __str__(self):
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
               "TOTAL BALANCE: {8} DKK".format(self.total_income(), self.dinner_income(), self.shopping_income(),
                                               self.beverage_income(), self.total_expenses(), self.dinner_expenses(),
                                               self.shopping_expenses(), self.beverage_expenses(), self.total_balance())

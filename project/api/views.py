from sqlalchemy.sql import label
from sqlalchemy.exc import DBAPIError

from project.api import api
from flask import request, jsonify
from datetime import datetime, date
from project.models import db, Dinner, User, Beverage, BeverageBatch, BeverageUser


@api.route('/')
def index():
    return "{results: bla}"


@api.route('/dinners')
def dinners():
    start = request.args.get('start')
    end = request.args.get('end')

    start = datetime.strptime(start, "%Y-%m-%d") if start else datetime.now()
    end = datetime.strptime(end, "%Y-%m-%d") if end else datetime.strptime("3000-01-01 23:59:59", "%Y-%m-%d %H:%M:%S")

    dinners = db.session.query(
        label("start", Dinner.date),
        label("title", User.name),
        label("url", Dinner.id)
    ).filter(
        Dinner.date >= start,
        Dinner.date <= end,
        Dinner.payee_id.is_(User.id)
    ).group_by(Dinner.id).all()
    return jsonify(dinners=dinners)


@api.route('/is_user', methods=['GET', 'POST'])
def is_user():
    if 'user_id' and 'beverage_id' in request.args:
        user_id = int(request.args['user_id'])
        beverage_id = int(request.args['beverage_id'])
    else:
        return "Error: No user_id field provided"

    # Checks if the user is in our DB
    results = User.query.get(user_id)
    if results:

        # Check if beverage exists
        beverage = Beverage.query.get(beverage_id)
        if beverage:

            # Check if there are any left
            beverage_batch = BeverageBatch.query.filter(
                BeverageBatch.quantity != 0
            ).filter_by(
                beverage_id=beverage_id
            ).first()
            if beverage_batch:
                # Handling beverage transaction
                try:
                    # decrementing quantity
                    beverage_batch.quantity = beverage_batch.quantity - 1

                    # assigning beer
                    bought_beverage = BeverageUser(beverage_batch_id=beverage_batch.id, user_id=user_id)
                    db.session.add(bought_beverage)
                    db.session.commit()
                    return "Success: A beverage was bought"
                except DBAPIError as e:
                    db.session.rollback()
                    return "Error: A beverage could not be bought. Try again or contact an admin"
            else:
                return "Error: It appears that there are no more beers left. Contact an admin."
        else:
            return "Error: Beverage does not exist."
    else:
        return "Error: User does not exist. Try again or contact an admin."

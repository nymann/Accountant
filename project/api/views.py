from sqlalchemy.sql import label

from project.api import api
from flask import request, jsonify
from datetime import datetime, date
from project.models import db, Dinner, User


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
        label("title", User.name),
        label("url", Dinner.id),
        label("start", Dinner.date)
    ).filter(
        Dinner.date >= start,
        Dinner.date <= end,
        Dinner.payee_id.is_(User.id)
    ).group_by(Dinner.id).all()
    return jsonify(dinners)

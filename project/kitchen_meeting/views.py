from flask import render_template

from collections import Counter
from datetime import datetime

from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user
from sqlalchemy.exc import DBAPIError
from sqlalchemy.sql import label

from project.kitchen_meeting import kitchen_meeting
from project.forms import MeetingForm
from project.models import User, Dinner, GuestAssociation, MeetingTopics
from project.models import db


@kitchen_meeting.route('/')
def index():
    form = MeetingForm()
    query = MeetingTopics.query.filter(
        MeetingTopics.talked_about.is_(False)
    )
    print(str(query))
    topics = query.all()
    return render_template('kitchen_meeting/index.html', topics=topics, form=form)

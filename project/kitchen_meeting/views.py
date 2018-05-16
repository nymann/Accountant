from flask import render_template, flash
from sqlalchemy.exc import DBAPIError
from flask_login import current_user, login_required

from project.forms import MeetingForm
from project.kitchen_meeting import kitchen_meeting
from project.models import MeetingTopic, db


@kitchen_meeting.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = MeetingForm()

    if form.validate_on_submit():
        meeting_topic = MeetingTopic(topic=form.topic.data)
        try:
            db.session.add(meeting_topic)
            db.session.commit()
            flash("Meeting Topic added successfully", "alert alert-info")
        except DBAPIError as e:
            db.session.rollback()
            flash(str(e), "alert alert-danger")

    topics = MeetingTopic.query.filter(
        MeetingTopic.talked_about.is_(False)
    ).all()

    return render_template('kitchen_meeting/index.html', topics=topics, form=form)

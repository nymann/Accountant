from flask import render_template, flash
from sqlalchemy.exc import DBAPIError
from flask_login import login_required, current_user

from project.forms import MeetingForm
from project.kitchen_meeting import kitchen_meeting
from project.models import MeetingTopic, db


@kitchen_meeting.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = MeetingForm()

    if form.validate_on_submit():
        if form.topic.data.strip() == "":
            flash("Please don't leave the textfield blank...", "alert alert-danger")
        else:
            meeting_topic = MeetingTopic(topic=form.topic.data, user_id=current_user.id)
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

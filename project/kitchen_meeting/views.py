from flask import render_template, flash
from sqlalchemy.exc import DBAPIError
from flask_login import login_required, current_user

from project.forms import MeetingTopicForm, MeetingEventForm
from project.kitchen_meeting import kitchen_meeting
from project.models import MeetingTopic, MeetingEvent, db


@kitchen_meeting.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = MeetingTopicForm()

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

    event = MeetingEvent.query.filter(
        MeetingEvent.completed.is_(False)
    ).order_by(
        MeetingEvent.id.desc()
    ).first()

    return render_template('kitchen_meeting/index.html', topics=topics, form=form, event=event)


@kitchen_meeting.route('/new', methods=['GET', 'POST'])
@login_required
def new_meeting():
    form = MeetingEventForm()
    if form.validate_on_submit():
        meeting_event = MeetingEvent(date=form.date.data);
        print(form.date.data)
        try:
            db.session.add(meeting_event)
            db.session.commit()
            flash("Meeting created", "alert alert-info")
        except DBAPIError as e:
            db.session.rollback()
            flash(str(e), "alert alert-danger")

    topics = MeetingTopic.query.filter(
        MeetingTopic.talked_about.is_(False)
    ).all()

    event = MeetingEvent.query.filter(
        MeetingEvent.completed.is_(False)
    ).order_by(
        MeetingEvent.id.desc()
    ).first()

    return render_template('kitchen_meeting/index.html', topics=topics, form=form, event=event)


@kitchen_meeting.route('/meeting', methods=['GET', 'POST'])
@login_required
def execute_meeting():
    # Some kind of logic, to assign all topics, to the active meeting.

    event = MeetingEvent.query.filter(
        MeetingEvent.completed.is_(False)
    ).order_by(
        MeetingEvent.id.desc()
    ).first()

    # This should only return the topics, which links
    # tot his meeting.
    topics = MeetingTopic.query.filter(
        MeetingTopic.talked_about.is_(False)
    ).all()

    return render_template('kitchen_meeting/meeting.html', event=event, topics=topics)

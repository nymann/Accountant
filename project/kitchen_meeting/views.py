from flask import render_template, flash, request
from sqlalchemy.exc import DBAPIError
from flask_login import login_required, current_user

from project.forms import MeetingTopicForm, MeetingEventForm
from project.kitchen_meeting import kitchen_meeting
from project.models import MeetingTopic, MeetingEvent, db
from datetime import datetime


@kitchen_meeting.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = MeetingTopicForm()

    topics = MeetingTopic.query.filter(
        MeetingTopic.talked_about.is_(False)
    ).all()

    event = MeetingEvent.query.filter(
        MeetingEvent.completed.is_(False)
    ).order_by(
        MeetingEvent.id.desc()
    ).first()

    return render_template('kitchen_meeting/index.html', topics=topics, form=form, event=event)


@kitchen_meeting.route('/new_topic', methods=['GET', 'POST'])
@login_required
def new_topic():
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

    return index()


@kitchen_meeting.route('/new', methods=['GET', 'POST'])
@login_required
def new_meeting():
    form = MeetingEventForm()
    if form.validate_on_submit():
        meeting_event = MeetingEvent(date=datetime.strptime(form.date.data, "%d/%m/%Y").date())
        print(form.date.data)
        try:
            db.session.add(meeting_event)
            db.session.commit()
            flash("Meeting created", "alert alert-info")
        except DBAPIError as e:
            db.session.rollback()
            flash(str(e), "alert alert-danger")

    return index()


@kitchen_meeting.route('/meeting', methods=['GET', 'POST'])
@login_required
def execute_meeting():
    event = MeetingEvent.query.filter(
        MeetingEvent.completed.is_(False)
    ).order_by(
        MeetingEvent.id.desc()
    ).first()

    topics = MeetingTopic.query.filter(
        MeetingTopic.talked_about.is_(False)
    ).all()

    return render_template('kitchen_meeting/meeting.html', event=event, topics=topics)


@kitchen_meeting.route('/done', methods=['GET', 'POST'])
@login_required
def finishing_meeting():
    topic_ids = request.form.getlist("mark_topics")

    event = MeetingEvent.query.filter(
        MeetingEvent.completed.is_(False)
    ).order_by(
        MeetingEvent.id.desc()
    ).first()

    try:
        # Topic get closed and assigned to Meeting event
        for topic_id in topic_ids:
            topic = MeetingTopic.query.filter_by(id=topic_id).first()
            topic.talked_about = True
            topic.meeting_id = event.id
            db.session.commit()

        # Event get closed
        event.completed = True
        db.session.commit()
        flash("Meeting resolved succesfully", "alert alert-info")
    except DBAPIError as e:
        db.session.rollback()
        flash(str(e), "alert alert-danger")

    return index()

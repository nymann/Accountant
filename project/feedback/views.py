from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, login_required
from sqlalchemy.exc import DBAPIError

from project.feedback import feedback
from project.forms import FeedbackForm
from project.models import db, Feedback, FeedbackComment


@feedback.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = FeedbackForm()
    # if current_user.admin:
    #     return render_template('feedback/feedback_admin.html')

    feedbacks = Feedback.query.all()

    return render_template('feedback/index.html', form=form, feedbacks=feedbacks)


@feedback.route('/admin', methods=['GET', 'POST'])
@login_required
def feedback_admin():
    render_template('feedback/feedback_admin.html')


@feedback.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback_user():
    form = FeedbackForm()

    if form.validate_on_submit():
        # Get data from form
        header = form.feedback_header.data
        user_id = current_user.id
        label = form.feedback_label.data
        comment = form.feedback_description.data

        try:
            feedback = Feedback(header=header, author=user_id, label=label)
            db.session.add(feedback)
            db.session.commit()

            feedback_comment = FeedbackComment(feedback_id=feedback.id, author=user_id, comment=comment)
            db.session.add(feedback_comment)
            db.session.commit()
            flash("Your feedback has been filed. Thank you!", "alert alert-info")
        except DBAPIError as e:
            flash(str(e), "alert alert-danger")
            db.session.rollback()

    return index()


@feedback.route('/feedback/<feedback_id>', methods=['GET', 'POST'])
@login_required
def feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)

    feedback_comments = FeedbackComment.query.filter(
        FeedbackComment.feedback_id == feedback_id
    ).all()

    return render_template('feedback/feedback.html', feedback=feedback, feedback_comments=feedback_comments)

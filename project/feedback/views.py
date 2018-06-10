from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, login_required
from sqlalchemy.exc import DBAPIError

from project.forms import FeedbackForm
from project.models import db, Feedback, FeedbackComment
from project.site import site


@site.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = FeedbackForm()

    if current_user.admin:
        return render_template('site/feedback_admin.html', form=form)

    if form.validate_on_submit():
        # Get data from form
        header = form.feedback_header.data
        user_id = current_user.id
        label = form.feedback_label.data
        messages = form.feedback_description.data

        try:
            feedback = Feedback(header=header, author=user_id, label=label)
            db.session.add(feedback)
            db.session.commit()

            feedback_comment = FeedbackComment(feedback_id=feedback.id, author=user_id, messages=messages)
            db.session.add(feedback_comment)
            db.session.commit()
            flash("Your feedback has been filed. Thank you!", "alert alert-true")
        except DBAPIError as e:
            flash(str(e), "alert alert-danger")
            db.session.rollback()

    return render_template('feedback/index.html', form=form)

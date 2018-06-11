from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, login_required
from sqlalchemy.exc import DBAPIError

from project.feedback import feedback
from project.forms import FeedbackForm, FeedbackCommentForm
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


@feedback.route('/feedback/<feedback_id>/comment', methods=['POST'])
@login_required
def add_feedback_comment(feedback_id):
    form = FeedbackCommentForm()

    if form.validate_on_submit():

        feedback_comment = FeedbackComment(feedback_id=feedback_id, author=current_user.id,
                                           comment=form.feedback_comment.data)
        print(form.feedback_comment.data)
        try:
            db.session.add(feedback_comment)
            db.session.commit()
            flash("Your comment have been successfully added", "alert alert-info")
        except DBAPIError as e:
            flash(str(e), "alert alert-danger")
            db.session.rollback()

    # return redirect(url_for('feedback.feedback', feedback_id=feedback_id), code=200)
    return index()


@feedback.route('/feedback/<int:feedback_id>', methods=['GET', 'POST'])
@login_required
def feedback(feedback_id):
    form = FeedbackCommentForm()
    feedback = Feedback.query.get(feedback_id)

    query = FeedbackComment.query.filter(
        FeedbackComment.feedback_id == feedback_id
    ).order_by(
        FeedbackComment.timestamp
    )

    first_comment = query.first()
    feedback_comments = query.all()[1:]

    return render_template(
        'feedback/feedback.html', feedback=feedback, feedback_comments=feedback_comments, first_comment=first_comment,
        form=form
    )

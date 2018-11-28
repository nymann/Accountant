from flask_mail import Message, Mail

from project import app


def send_an_email(recipients, body, header):
    app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = app.config.get('MAIL_USERNAME')  # enter your email here
    app.config['MAIL_DEFAULT_SENDER'] = app.config.get('MAIL_USERNAME')  # enter your email here
    app.config['MAIL_PASSWORD'] = app.config.get('MAIL_PASSWORD')  # enter your password here
    mail = Mail()
    mail.init_app(app)

    msg = Message(header,
                  recipients=recipients)
    msg.html = body

    mail.send(msg)

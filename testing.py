from flask_mail import Message, Mail

from project import app


def send_an_email():
    msg = Message("Hello",
                  sender="from@example.com",
                  recipients=["thyge.steffensen@hotmail.com"])
    mail = Mail()

    app.config['SECRET_KEY'] = 'a really really really really long secret key'
    app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'thyge.skoedt@gmail.com'  # enter your email here
    app.config['MAIL_DEFAULT_SENDER'] = 'thyge.skoedt@gmail.com'  # enter your email here
    app.config['MAIL_PASSWORD'] = 'zvcgjokoygapkxvv'  # enter your password here

    mail.init_app(app)

    mail.send(msg)

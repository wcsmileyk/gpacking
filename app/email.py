from flask_mail import Message
from . import app, mail


def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['GPACKING_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['GPACKING_MAIL_SENDER'],
                  recipients=[to]
                  )
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)

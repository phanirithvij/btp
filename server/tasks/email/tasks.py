from server.tasks import celery, logger


from flask import current_app, render_template
from flask_mail import Message

# https://github.com/miguelgrinberg/flasky-with-celery/issues/7

@celery.task
def send_async_email(msg_dict):
    # msg = Message()
    # msg.__dict__.update(msg_dict)
    mail.send(msg_dict)


@celery.task
def send_async_emails(msg_dicts):
    with mail.connect() as conn:
        for msg_dict in msg_dicts:
            msg = Message()
            msg.__dict__.update(msg_dict)
            conn.send(msg)

def msg_to_pickle(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(
        subject=app.config['Unnamed_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
        sender=app.config['Unnamed_MAIL_SENDER'],
        recipients=[to]
    )
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    return msg
    # return msg.__dict__


def send_email(to, subject, template, **kwargs):
    send_async_email.apply_async((msg_to_pickle(to, subject, template, **kwargs),), serializer='pickle')
    # send_async_email.apply_async(msg_to_pickle(to, subject, template, **kwargs), serializer='pickle')


def send_emails(users, subject, template, **kwargs):
    send_async_emails.apply_async([msg_to_pickle(
        to=user.email, subject=subject, template=template, **kwargs) for user in users])

from __future__ import absolute_import # for Celery

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

try:
    from main.celery import app as celery_app
    celery = True
except ImportError:
    celery = False


class Mail:
    """
    Email sending helper class, that handles:
    - templates for body/subject
    - sync/async (if Celery is enabled) sending
    #- status from SendGrid ("delivered", "bounce", ...)
    """

    template_subject_suffix = '_subject.txt'
    template_message_suffix = '_body.txt'
    template_message_html_suffix = '_body.html'

    def __init__(self, *args, **kwargs):
        self.recipient_list = kwargs.get('recipient_list', [])
        self.sender = kwargs.get('sender', getattr(settings, 'DEFAULT_FROM_EMAIL', None))

        self.subject = kwargs.get('subject', '')
        self.message = kwargs.get('message', '')
        self.message_html = kwargs.get('message_html', '')

        self.template_name = kwargs.get('template_name', None)
        self.context = kwargs.get('context', {})

        self.fail_silently = kwargs.get('fail_silently', True)

    def send(self):
        if celery:
            send_mail_task.delay(self)
        else:
            self._send()

    def _send(self):
        # TODO: add support for html messages
        if self.template_name:
            subject = render_to_string(
                self.template_name + Mail.template_subject_suffix,
                self.context).strip()
            message = render_to_string(
                self.template_name + Mail.template_message_suffix,
                self.context)
        else:
            subject = self.subject
            message = self.message

        result = send_mail(subject, message, self.sender, self.recipient_list, 
                                                fail_silently=self.fail_silently)


# @shared_task # loaddata doesn't handle it :(
@celery_app.task
def send_mail_task(mail):
    """
    Send email (via Sendgird or other way)
    (called asynchronosly via Celery)
    """
    mail._send()

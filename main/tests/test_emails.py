# test mailgun email
from django.test import TestCase
from django.core.mail import send_mail
from django.conf import settings


class EmailsTests(TestCase):

    def test_send_email(self):
        sent = send_mail("Mailgun Email Test", "One beautiful body", settings.DEFAULT_FROM_EMAIL,
          ['betasmartz.jenkins@gmail.com'], html_message="<html>One beautiful email</html>")
        self.assertEqual(sent, 1)

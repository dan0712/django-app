# -*- coding: utf-8 -*-
from rest_framework import status
from django.core import mail
from rest_framework.test import APIClient, APITestCase
from .factories import UserFactory, SecurityAnswerFactory


class PasswordsTests(APITestCase):
    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)
        self.user = UserFactory.create()
        self.user2 = UserFactory.create()
        self.user3 = UserFactory.create()
        self.sa = SecurityAnswerFactory.create(user=self.user2)

    def tearDown(self):
        self.client.logout()

    def _get_token(self, url, data):
        resp = self.client.get(url)
        data['csrfmiddlewaretoken'] = resp.cookies['csrftoken'].value
        return data

    # tests against api.v1.user.views.PasswordResetView
    def test_reset_password(self):
        """
        Test that unauthenticated requests for current user accounts
        can reset their password.  Does not test email backend.
        """
        # test good request
        url = '/password/reset/'
        data = {
            'email': self.user.email,
        }
        data = self._get_token(url, data)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='200 returned by reset password request')
        self.assertEqual(mail.outbox[0].subject, 'Password reset on testserver',
                         msg='Email outbox has email with expected subject')

        # ok lets test a bad request and make sure we get a 401
        data = {
            'email': 'boatymcboatface@ukboats.com',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
                         msg='401 for valid emails not associated with any users')

        # test non-email returns 401
        data = {
            'email': 'boatymcboatface',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
                         msg='401 for invalid emails addresses')

        # test empty email returns 401
        data = {
            'email': '',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
                         msg='401 for empty email addresses')

    # tests against api.v1.user.views.ChangePasswordView
    def test_change_password(self):
        """
        Test that an authenticated user can change their password.
        """
        url = '/api/v1/me/password/'
        # userfactory has test for password on new users by default
        old_password = 'test'
        new_password = 'test2'

        data = {
            'old_password': old_password,
            'new_password': new_password,
            'answer': self.sa.answer,
        }
        # check for 403 on an unauthenticated request first
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                         msg='403 for unauthenticated requests to change password')

        # authenticate and check for good request
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='200 returned by authenticated change password request')

        # ok, lets check these passwords out
        self.assertTrue(self.user2.check_password(new_password))

        # ok, lets test authenticated bad requests
        # old password mismatch
        data = {
            'old_password': 'Batman Forever',
            'new_password': 'Batman The DarK Knight',
            'answer': self.sa.answer,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
                         msg='401 returned by wrong password from authenticated change password request')

        # security answer mismatch
        # going to grab a new user and re-authenticate
        # don't want to keep reusing data here

        data = {
            'old_password': 'test',
            'new_password': 'joker',
            'answer': 'This is the wrong answer',
        }
        self.client.force_authenticate(user=self.user3)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
                         msg='401 for authenticated request to change password with wrong security answer')

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from common.constants import GROUP_SUPPORT_STAFF
from main.constants import ACCOUNT_TYPES
from main.models import User
from main.tests.fixture import Fixture1
from .factories import AdvisorFactory, SecurityQuestionFactory, \
    EmailInviteFactory
from client.models import EmailInvite



class InviteTests(APITestCase):
    def setUp(self):
        self.advisor = AdvisorFactory.create()

    def tearDown(self):
        self.client.logout()

    def test_register_with_invite_key(self):
        # Bring an invite key, get logged in as a new user
        invite = EmailInviteFactory.create(status=EmailInvite.STATUS_SENT)
        question_one = SecurityQuestionFactory.create()
        question_two = SecurityQuestionFactory.create()

        url = reverse('api:v1:client-user-register')
        data = {
            'first_name': invite.first_name,
            'last_name': invite.last_name,
            'invite_key': invite.invite_key,
            'email': invite.email,
            'password': 'test',
            'question_one_id': question_one.id,
            'question_one_answer': 'answer one',
            'question_two_id': question_two.id,
            'question_two_answer': 'answer two',
        }

        # 400 no such token=123
        response = self.client.post(url, dict(data, invite_key='123'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg='400 for registrations from nonexistant email invite')

        # 400 on bad securityquestions
        response = self.client.post(url, dict(data, question_one_id=9999))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg='400 on bad question id')
        response = self.client.post(url, dict(data, question_two_id=9999))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg='400 on bad question id')
        response = self.client.post(url, dict(data, question_one_answer=''))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg='400 on bad question answer')
        response = self.client.post(url, dict(data, question_two_answer=''))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg='400 on bad question answer')

        # 400 token must match user
        response = self.client.post(url, dict(data, email='invalid@example.org'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg='400 for registrations from mismatched email invite')

        # With a valid token, get a valid user
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='Register a valid invitation is 200 OK')
        self.assertNotEqual(response.data['id'], None,
                         msg='Registering an invitation should give valid user_id')

        lookup_invite = EmailInvite.objects.get(pk=invite.pk)
        self.assertEqual(response.data['email'], invite.email,
                         msg='New users email should match invitation')
        self.assertEqual(response.data['id'], lookup_invite.user.id,
                         msg='New users id should match invitation')
        self.assertEqual(EmailInvite.STATUS_ACCEPTED, lookup_invite.status)

        # New user must be logged in too
        self.assertIn('sessionid', response.cookies)


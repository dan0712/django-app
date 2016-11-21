import os
import json
from datetime import date
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from address.models import Region
from api.v1.tests.factories import AdvisorFactory, EmailInviteFactory
from client.models import EmailInvite
from django.test import Client as DjangoClient
from common.constants import GROUP_SUPPORT_STAFF
from .factories import AccountTypeRiskProfileGroupFactory, AddressFactory, \
    ClientAccountFactory, ClientFactory, ExternalAssetFactory, GoalFactory, \
    GroupFactory, RegionFactory, RiskProfileGroupFactory, UserFactory
from django.core import mail

class SupportTests(APITestCase):
    def setUp(self):
        self.support_group = GroupFactory(name=GROUP_SUPPORT_STAFF)
        self.betasmartz_client = ClientFactory.create()

    def test_request_advisor_support(self):
        url = '/api/v1/support-requests'
        self.client.force_authenticate(self.betasmartz_client.user)
        data = {
            'url': 'example.com',
            'text': 'How do I proceed without such and such?',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(mail.outbox[0].subject, 'Client Requests Support',
                         msg='Email outbox has email with expected subject')

    def test_request_advisor_support_no_text(self):
        url = '/api/v1/support-requests'
        self.client.force_authenticate(self.betasmartz_client.user)
        data = {
            'url': 'example.com',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(mail.outbox[0].subject, 'Client Requests Support',
                         msg='Email outbox has email with expected subject')

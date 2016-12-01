# -*- coding: utf-8 -*-
from django.test import TestCase
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse
from main import constants
from api.v1.tests.factories import ClientAccountFactory, \
    ClientFactory, GoalFactory, \
    TransactionFactory, AccountTypeRiskProfileGroupFactory, \
    ExternalAssetFactory, TickerFactory, \
    SupervisorFactory, AuthorisedRepresentativeFactory, \
    InvestmentTypeFactory, PositionLotFactory, \
    ExternalAssetFactory, TickerFactory, \
    GroupFactory, AdvisorFactory
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from rest_framework import status
from common.constants import GROUP_SUPPORT_STAFF


class PrivacyPolicyTests(TestCase):
    def test_get_privacy_policy(self):
        url = reverse('privacy_policy')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

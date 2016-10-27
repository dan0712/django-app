# -*- coding: utf-8 -*-
from django.test import TestCase
from rest_framework import status
from api.v1.tests.factories import TransactionFactory, PlatformFactory
from main.models import User


class BetasmartzAdminTests(TestCase):
    def setUp(self):
        # self.user = SuperUserFactory.create()
        self.user = User.objects.create_superuser('superadmin', 'superadmin@example.com', 'test')
        self.platform = PlatformFactory.create()
        self.transaction = TransactionFactory.create()

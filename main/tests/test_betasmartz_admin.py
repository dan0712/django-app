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

    def test_execute_transaction(self):
        url = '/betasmartz_admin/transaction/{}/execute'.format(self.transaction.id)
        login = self.client.login(username=self.user.email, password='test')
        self.assertEqual(login, True)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

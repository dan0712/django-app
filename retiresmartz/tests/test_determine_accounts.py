from datetime import datetime, timedelta
from unittest import mock
from django.test import TestCase
from django.utils import timezone
from api.v1.tests.factories import RetirementPlanFactory, \
    RetirementPlanAccountFactory, ClientAccountFactory, ClientFactory
from retiresmartz.models import RetirementPlan, determine_accounts
from main.tests.fixture import Fixture1
from main import constants
from dateutil.relativedelta import relativedelta


class RetiresmartzTestCase(TestCase):
    def setUp(self):

        # employed, client over 50 years old
        self.betasmartz_client = ClientFactory.create(employment_status=constants.EMPLOYMENT_STATUS_FULL_TIME,
                                                      date_of_birth=datetime.now().date() - relativedelta(years=60))
        self.betasmartz_client.regional_data['tax_transcript_data'] = {'sections': [{'name': 'Introduction', 'fields': {'SPOUSE NAME': 'SPOUSE M LAST', 'SPOUSE SSN': '222-22-2222', 'ADDRESS': '999 AVENUE RD  CITY, ST 10.000-90.00-800', 'NAME': 'FIRST M', 'SSN': '111-11-1111', 'FILING STATUS': 'Single'}}, {'name': 'Income', 'fields': {'TOTAL INCOME': '$0.00'}}]}
        self.betasmartz_client.save()
        # personal account
        self.account = ClientAccountFactory.create(primary_owner=self.betasmartz_client)
        self.plan = RetirementPlanFactory.create(client=self.betasmartz_client)
        self.plan_account = RetirementPlanAccountFactory.create(plan=self.plan,
                                                                account=self.account)

        # 401k
        self.account2 = ClientAccountFactory.create(primary_owner=self.betasmartz_client, account_type=constants.ACCOUNT_TYPE_401K)
        self.plan2 = RetirementPlanFactory.create(client=self.betasmartz_client,
                                                  income=100000,
                                                  max_employer_match_percent=.05)
        self.plan_account2 = RetirementPlanAccountFactory.create(plan=self.plan2,
                                                                account=self.account2)

        # roth IRA
        self.account5 = ClientAccountFactory.create(primary_owner=self.betasmartz_client, account_type=constants.ACCOUNT_TYPE_ROTHIRA)
        self.plan5 = RetirementPlanFactory.create(client=self.betasmartz_client,
                                                  income=100000,
                                                  max_employer_match_percent=.05)
        self.plan_account5 = RetirementPlanAccountFactory.create(plan=self.plan5,
                                                                account=self.account5)

        # unemployed, client 40 years old
        self.unemployed_client = ClientFactory.create(employment_status=constants.EMPLOYMENT_STATUS_UNEMPLOYED,
                                                      date_of_birth=datetime.now().date() - relativedelta(years=40))
        self.unemployed_client.regional_data['tax_transcript_data'] = {'sections': [{'name': 'Introduction', 'fields': {'SPOUSE NAME': 'SPOUSE M LAST', 'SPOUSE SSN': '222-22-2222', 'ADDRESS': '999 AVENUE RD  CITY, ST 10.000-90.00-800', 'NAME': 'FIRST M', 'SSN': '111-11-1111', 'FILING STATUS': 'Single'}}, {'name': 'Income', 'fields': {'TOTAL INCOME': '$0.00'}}]}
        self.unemployed_client.save()
        # personal account
        self.account3 = ClientAccountFactory.create(primary_owner=self.unemployed_client)
        self.plan3 = RetirementPlanFactory.create(client=self.unemployed_client)
        self.plan_account3 = RetirementPlanAccountFactory.create(plan=self.plan3,
                                                                account=self.account3)

        # employed, client over 50 years old, 150k+ income
        self.betasmartz_client2 = ClientFactory.create(employment_status=constants.EMPLOYMENT_STATUS_FULL_TIME,
                                                      date_of_birth=datetime.now().date() - relativedelta(years=60))
        self.betasmartz_client2.regional_data['tax_transcript_data'] = {'sections': [{'name': 'Introduction', 'fields': {'SPOUSE NAME': 'SPOUSE M LAST', 'SPOUSE SSN': '222-22-2222', 'ADDRESS': '999 AVENUE RD  CITY, ST 10.000-90.00-800', 'NAME': 'FIRST M', 'SSN': '111-11-1111', 'FILING STATUS': 'Single'}}, {'name': 'Income', 'fields': {'TOTAL INCOME': '$0.00'}}]}
        self.betasmartz_client2.save()

        # personal account
        self.account6 = ClientAccountFactory.create(primary_owner=self.betasmartz_client2)
        self.plan6 = RetirementPlanFactory.create(client=self.betasmartz_client2,
                                                  income=150000)
        self.plan_account6 = RetirementPlanAccountFactory.create(plan=self.plan6,
                                                                account=self.account6)

        # 401k
        self.account7 = ClientAccountFactory.create(primary_owner=self.betasmartz_client2, account_type=constants.ACCOUNT_TYPE_401K)
        self.plan7 = RetirementPlanFactory.create(client=self.betasmartz_client2,
                                                  income=150000,
                                                  max_employer_match_percent=.05)
        self.plan_account7 = RetirementPlanAccountFactory.create(plan=self.plan7,
                                                                account=self.account7)

        # roth IRA
        self.account8 = ClientAccountFactory.create(primary_owner=self.betasmartz_client2, account_type=constants.ACCOUNT_TYPE_ROTHIRA)
        self.plan8 = RetirementPlanFactory.create(client=self.betasmartz_client2,
                                                  income=150000,
                                                  max_employer_match_percent=.05)
        self.plan_account8 = RetirementPlanAccountFactory.create(plan=self.plan8,
                                                                account=self.account8)

        # unemployed, client 40 years old 150k+ income
        self.unemployed_client2 = ClientFactory.create(employment_status=constants.EMPLOYMENT_STATUS_UNEMPLOYED,
                                                      date_of_birth=datetime.now().date() - relativedelta(years=40))
        self.unemployed_client2.regional_data['tax_transcript_data'] = {'sections': [{'name': 'Introduction', 'fields': {'SPOUSE NAME': 'SPOUSE M LAST', 'SPOUSE SSN': '222-22-2222', 'ADDRESS': '999 AVENUE RD  CITY, ST 10.000-90.00-800', 'NAME': 'FIRST M', 'SSN': '111-11-1111', 'FILING STATUS': 'Single'}}, {'name': 'Income', 'fields': {'TOTAL INCOME': '$0.00'}}]}
        self.unemployed_client2.save()
        # personal account
        self.account9 = ClientAccountFactory.create(primary_owner=self.unemployed_client2)
        self.plan9 = RetirementPlanFactory.create(client=self.unemployed_client2,
                                                  income=150000)
        self.plan_account9 = RetirementPlanAccountFactory.create(plan=self.plan9,
                                                                account=self.account9)


    def test_account_must_be_confirmed(self):
        account = Fixture1.personal_account1()

    def test_determine_accounts_100k_income(self):
        # full time employed personal 100k income
        account_contributions = determine_accounts(self.plan)
        self.assertEqual(len(account_contributions), 9)
        expected = [(8, 6500), (6, 18000), (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (7, 0)]
        self.assertEqual(account_contributions, expected)

        # 401 full time employed
        account_contributions = determine_accounts(self.plan2)
        self.assertEqual(len(account_contributions), 9)
        expected = [(5, 18000), (8, 6500), (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (6, 0), (7, 0)]
        self.assertEqual(account_contributions, expected)

        # roth IRA full time employed 100k income
        account_contributions = determine_accounts(self.plan5)
        self.assertEqual(len(account_contributions), 9)

        # unemployed personal
        account_contributions = determine_accounts(self.plan3)
        self.assertEqual(len(account_contributions), 9)
        expected = [(7, 6600), (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (8, 0)]
        self.assertEqual(account_contributions, expected)


    def test_determine_accounts_150k_income(self):
        # full time employed personal 150k income
        account_contributions = determine_accounts(self.plan6)
        self.assertEqual(len(account_contributions), 9)
        expected = [(5, 18000), (7, 6500), (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (6, 0), (8, 0)]
        self.assertEqual(account_contributions, expected)

        # 401 full time employed
        account_contributions = determine_accounts(self.plan7)
        self.assertEqual(len(account_contributions), 9)
        expected =  [(5, 18000), (7, 18000), (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (6, 0), (8, 0)]
        self.assertEqual(account_contributions, expected)

        # roth IRA full time employed 150k income
        account_contributions = determine_accounts(self.plan8)
        self.assertEqual(len(account_contributions), 9)

        # unemployed personal
        account_contributions = determine_accounts(self.plan9)
        self.assertEqual(len(account_contributions), 9)
        expected = [(7, 6600), (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (8, 0)]
        self.assertEqual(account_contributions, expected)


from datetime import datetime, timedelta
from unittest import mock

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from retiresmartz.models import RetirementPlan
from main.tests.fixture import Fixture1


class RetiresmartzTestCase(TestCase):
    def test_account_must_be_confirmed(self):
        account = Fixture1.personal_account1()

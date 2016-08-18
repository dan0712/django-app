import uuid

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from phonenumber_field.modelfields import PhoneNumberField

from common.structures import ChoiceEnum


class PersonalData(models.Model):
    class Meta:
        abstract = True

    class CivilStatus(ChoiceEnum):
        SINGLE = 0
        MARRIED = 1  # May be married, or any other financially recognised relationship.

    date_of_birth = models.DateField(verbose_name="Date of birth", null=True)
    gender = models.CharField(max_length=20,
                              default="Male",
                              choices=(("Male", "Male"), ("Female", "Female")))
    residential_address = models.ForeignKey('address.Address', related_name='+')
    phone_num = PhoneNumberField(null=True, max_length=16)  # A person may not have a phone.
    medicare_number = models.CharField(max_length=50, default="")
    civil_status = models.IntegerField(null=True, choices=CivilStatus.choices())

    def __str__(self):
        return self.user.first_name + " - " + self.firm.name

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def name(self):
        return self.user.first_name + " " + self.user.last_name

    @property
    def states_codes(self):
        states = []
        for item in self._meta.get_field('state').choices:
            states.append({"db_value": item[0], "name": item[1]})
        return states

    @property
    def email(self):
        return self.user.email


class NeedApprobation(models.Model):
    class Meta:
        abstract = True

    is_accepted = models.BooleanField(default=False, editable=False)

    def approve(self):
        if self.is_accepted is True:
            return
        self.is_accepted = True
        self.save()
        self.send_approve_email()

    def send_approve_email(self):
        account_type = self._meta.verbose_name

        subject = "Your BetaSmartz new {0} account have been approved".format(
            account_type)

        context = {
            'subject': subject,
            'account_type': account_type,
            'firm_name': self.firm.name
        }

        send_mail(subject,
                  '',
                  None,
                  [self.email],
                  html_message=render_to_string('email/approve_account.html',
                                                context))


class NeedConfirmation(models.Model):
    class Meta:
        abstract = True

    confirmation_key = models.CharField(max_length=36,
                                        null=True,
                                        blank=True,
                                        editable=False)
    is_confirmed = models.BooleanField(default=False, editable=True)

    @property
    def content_type(self):
        return ContentType.objects.get_for_model(self).pk

    def get_confirmation_url(self):
        if self.is_confirmed is False:
            if self.confirmation_key is None:
                self.confirmation_key = str(uuid.uuid4())
                self.save()

        if self.is_confirmed or (self.confirmation_key is None):
            return None

        return settings.SITE_URL + "/confirm_email/{0}/{1}".format(
            self.content_type, self.confirmation_key)

    def send_confirmation_email(self):
        account_type = self._meta.verbose_name

        subject = "BetaSmartz new {0} account confirmation".format(
            account_type)

        context = {
            'subject': subject,
            'account_type': account_type,
            'confirmation_url': self.get_confirmation_url(),
            'firm_name': self.firm.name
        }

        send_mail(
            subject,
            '',
            None,
            [self.email],
            html_message=render_to_string('email/confirmation.html', context))


class TransferPlan(models.Model):
    begin_date = models.DateField()
    amount = models.IntegerField()
    growth = models.FloatField(
        help_text="Daily rate to increase or decrease the amount by as of"
                  " the begin_date. 0.0 for no modelled change")
    schedule = models.TextField(help_text="RRULE to specify "
                                          "when the transfer happens")

    class Meta:
        abstract = True


class FinancialInstrument(models.Model):
    """
    A financial instrument is an identifiable thing for which data can be gathered to generate a daily return.
    """
    class Meta:
        abstract = True

    display_name = models.CharField(max_length=255, blank=False, null=False, db_index=True)
    description = models.TextField(blank=True, default="", null=False)
    url = models.URLField()
    currency = models.CharField(max_length=10, default="AUD")
    region = models.ForeignKey('main.Region')
    data_api = models.CharField(help_text='The module that will be used to get the data for this ticker',
                                choices=[('portfolios.api.bloomberg', 'Bloomberg')],
                                max_length=30)
    data_api_param = models.CharField(help_text='Structured parameter string appropriate for the data api. The '
                                                'first component would probably be id appropriate for the given api',
                                      unique=True,
                                      max_length=30)

    def __str__(self):
        return self.display_name

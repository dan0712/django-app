__author__ = 'cristian'

from django.db import models
from main.models import Firm, Advisor, Client
from django_localflavor_au.models import AUStateField, AUPostCodeField, AUPhoneNumberField
from datetime import datetime

__all__ = ["ChangeDealerGroup", "SingleInvestorTransfer", "BulkInvestorTransfer"]


class ChangeDealerGroup(models.Model):
    advisor = models.ForeignKey(Advisor)
    old_firm = models.ForeignKey(Firm, related_name="old_advisors")
    new_firm = models.ForeignKey(Firm, related_name="new_advisors")
    approved = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True)
    work_phone = AUPhoneNumberField()
    letter_previous_group = models.FileField()
    letter_new_group = models.FileField()
    signature = models.FileField()

    def approve(self):
        self.approved = True
        self.advisor.firm = self.new_firm
        self.advisor.work_phone = self.work_phone
        """
        self.advisor.office_address_line_1 = self.office_address_line_1
        self.advisor.office_address_line_2 = self.office_address_line_2
        self.advisor.office_state = self.office_state
        self.advisor.office_city = self.office_city
        self.advisor.office_post_code = self.office_post_code
        self.advisor.postal_address_line_1 = self.postal_address_line_1
        self.advisor.postal_address_line_2 = self.postal_address_line_2
        self.advisor.postal_state = self.postal_state
        self.advisor.same_address = self.same_address
        self.advisor.postal_city = self.postal_city
        self.advisor.postal_post_code = self.postal_post_code
        self.advisor.daytime_phone_number = self.daytime_phone_number
        self.advisor.mobile_phone_number = self.mobile_phone_number
        self.advisor.fax_number = self.fax_number
        self.advisor.alternate_email_address = self.advisor.alternate_email_address
        """
        self.advisor.save()
        self.approved_at = datetime.now()
        self.save()


class SingleInvestorTransfer(models.Model):
    from_advisor = models.ForeignKey(Advisor)
    to_advisor = models.ForeignKey(Advisor, related_name="single_transfer_to_advisors")
    approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True)
    create_at = models.DateTimeField(auto_now_add=True)
    investor = models.ForeignKey(Client)
    signature_investor = models.FileField()
    signature_advisor = models.FileField()
    signature_joint_investor = models.FileField()

    def approve(self):
        self.investor.advisor = self.to_advisor
        self.investor.save()
        for account in self.investor.accounts.all():
            account.remove_from_group()
            account.save()
        self.approved = True
        self.approved_at = datetime.now()
        self.save()


class BulkInvestorTransfer(models.Model):
    from_advisor = models.ForeignKey(Advisor)
    to_advisor = models.ForeignKey(Advisor, related_name="bulk_transfer_to_advisors")
    approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True)

    create_at = models.DateTimeField(auto_now_add=True)
    bulk_investors_spreadsheet = models.ManyToManyField(Client)
    signature = models.FileField()

    def approve(self):
        for investor in self.bulk_investors_spreadsheet.all():
            investor.advisor = self.to_advisor
            investor.save()
            for account in investor.accounts.all():
                account.remove_from_group()
                account.save()

        self.approved = True
        self.approved_at = datetime.now()
        self.save()
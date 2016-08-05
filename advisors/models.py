from django.db import models
from django.utils.timezone import now
from phonenumber_field.modelfields import PhoneNumberField


class ChangeDealerGroup(models.Model):
    advisor = models.ForeignKey('main.Advisor')
    old_firm = models.ForeignKey('main.Firm', related_name="old_advisors")
    new_firm = models.ForeignKey('main.Firm', related_name="new_advisors")
    approved = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    work_phone = PhoneNumberField()
    new_email = models.EmailField()
    letter_previous_group = models.FileField(verbose_name="Prev. Group Letter")
    letter_new_group = models.FileField("New Group Letter")
    signature = models.FileField()

    def approve(self):
        self.approved = True
        self.advisor.firm = self.new_firm
        self.advisor.user.email = self.new_email
        self.advisor.work_phone_num = self.work_phone
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
        self.approved_at = now()
        self.save()


class SingleInvestorTransfer(models.Model):
    from_advisor = models.ForeignKey('main.Advisor')
    to_advisor = models.ForeignKey('main.Advisor', verbose_name="To Advisor", related_name="single_transfer_to_advisors")
    approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True)
    create_at = models.DateTimeField(auto_now_add=True)
    investor = models.ForeignKey('client.Client')
    firm = models.ForeignKey('main.Firm', editable=False)
    signatures = models.FileField()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        if self.pk is None:
            self.firm = self.from_advisor.firm

        return super(SingleInvestorTransfer, self).save(force_insert=False,
                                                        force_update=False, using=None, update_fields=None)

    def approve(self):
        self.investor.advisor = self.to_advisor
        self.investor.save()
        for account in self.investor.accounts.all():
            account.remove_from_group()
            account.save()
        self.approved = True
        self.approved_at = now()
        self.save()


class BulkInvestorTransfer(models.Model):
    from_advisor = models.ForeignKey('main.Advisor')
    to_advisor = models.ForeignKey('main.Advisor', verbose_name="To Advisor", related_name="bulk_transfer_to_advisors")
    approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True)
    firm = models.ForeignKey('main.Firm', editable=False)
    create_at = models.DateTimeField(auto_now_add=True)
    investors = models.ManyToManyField('client.Client')
    signatures = models.FileField()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        if self.pk is None:
            self.firm = self.from_advisor.firm

        return super(BulkInvestorTransfer, self).save(force_insert=False,
                                                      force_update=False, using=None, update_fields=None)

    def approve(self):
        for investor in self.investors.all():
            investor.advisor = self.to_advisor
            investor.save()
            for account in investor.accounts.all():
                account.remove_from_group()
                account.save()

        self.approved = True
        self.approved_at = now()
        self.save()


# noinspection PyUnresolvedReferences
from . import connectors

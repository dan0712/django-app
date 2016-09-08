import logging
from django.db import models
from jsonfield.fields import JSONField

logger = logging.getLogger('client.models')

class PDFStatement(models.Model):
    create_date = models.DateTimeField(auto_now_add=True)
    @property
    def date(self):
        return self.create_date.strftime('%Y-%m-%d_%H:%I:%S')

    @property
    def owner(self):
        return self.account.primary_owner

    @property
    def advisor(self):
        return self.owner.advisor

    @property
    def firm(self):
        return self.advisor.firm

    class Meta:
        abstract = True
        ordering = ('-create_date', )

class StatementOfAdvice(PDFStatement):
    account = models.OneToOneField('client.ClientAccount',
                        related_name='statement_of_advice')

    def __str__(self):
        return 'Statement of Advice for %s'%self.account

class RecordOfAdvice(PDFStatement):
    account = models.ForeignKey('client.ClientAccount',
                    related_name='records_of_advice')

    def __str__(self):
        return 'Record of Advice %s %s'%(self.account, self.date)

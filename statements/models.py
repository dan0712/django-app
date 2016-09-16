import logging
from django.db import models
from jsonfield.fields import JSONField
from weasyprint import HTML
from django.conf import settings

logger = logging.getLogger(__name__)

class PDFStatement(models.Model):
    create_date = models.DateTimeField(auto_now_add=True)
    @property
    def date(self):
        return self.create_date.strftime('%Y-%m-%d_%H:%I:%S')

    def render_template(self, template_name=None):
        from django.template.loader import render_to_string
        template_name = template_name or self.default_template
        return render_to_string(template_name, {
            'object': self,
            'statement': self,
            'account': self.account,
            'client': self.account.primary_owner,
            'owner': self.account.primary_owner,
            'advisor': self.account.primary_owner.advisor,
            'firm': self.account.primary_owner.advisor.firm,
        })

    def render_pdf(self, template_name=None):
        html = self.render_template(template_name)
        # Have to source the images locally for WeasyPrint
        static_path = settings.STATICFILES_DIRS[0]
        html = html.replace('/static/', 'file://%s/'%static_path)
        pdf_builder = HTML(string=html)
        return pdf_builder.write_pdf()

    @property
    def default_template(self):
        return None

    class Meta:
        abstract = True
        ordering = ('-create_date', )

class StatementOfAdvice(PDFStatement):
    account = models.OneToOneField('client.ClientAccount',
                        related_name='statement_of_advice')

    def __str__(self):
        return 'Statement of Advice for %s'%self.account

    @property
    def default_template(self):
        return "statements/statement_of_advice.html"

class RetirementStatementOfAdvice(PDFStatement):
    retirement_plan = models.OneToOneField('retiresmartz.RetirementPlan',
                        related_name='statement_of_advice')

    def __str__(self):
        return 'Statement of Advice for %s'%self.retirement_plan

    @property
    def account(self):
        return self.retirement_plan.smsf_account

    @property
    def default_template(self):
        return "statements/statement_of_advice.html"


class RecordOfAdvice(PDFStatement):
    account = models.ForeignKey('client.ClientAccount',
                    related_name='records_of_advice')

    def __str__(self):
        return 'Record of Advice %s %s'%(self.account, self.date)

    @property
    def default_template(self):
        return "statements/record_of_advice.html"

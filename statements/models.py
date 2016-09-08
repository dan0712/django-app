import logging
from django.db import models
from jsonfield.fields import JSONField
from weasyprint import HTML

logger = logging.getLogger('client.models')

class PDFStatement(models.Model):
    create_date = models.DateTimeField(auto_now_add=True)
    @property
    def date(self):
        return self.create_date.strftime('%Y-%m-%d_%H:%I:%S')

    def render_template(self, template_name):
        from django.template.loader import render_to_string
        return render_to_string(template_name, {
            'object': self,
            'statement': self,
            'account': self.account,
            'client': self.account.primary_owner,
            'owner': self.account.primary_owner,
            'advisor': self.account.primary_owner.advisor,
            'firm': self.account.primary_owner.advisor.firm,
        })

    def render_pdf(self, template_name):
        html = self.render_template(template_name)
        # Have to source the images locally for WeasyPrint
        html = html.replace('/static/', 'file:///betasmartz/static/')
        pdf_builder = HTML(string=html)
        return pdf_builder.write_pdf()

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

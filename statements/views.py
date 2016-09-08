__author__ = 'leeward'
from django.views.generic import DetailView
from django.http import HttpResponse
from django.conf import settings
from main.views.base import ClientView
from statements.models import StatementOfAdvice, RecordOfAdvice
from weasyprint import HTML

__all__ = ["StatementView", "RecordView"]


class PDFView(DetailView, ClientView):
    def get_queryset(self):
        return self.model.objects.filter(
            account__primary_owner=self.request.user.client)

    def get(self, request, pk, ext=None):
        response = super(PDFView, self).get(self, request, pk)
        obj = self.get_object()
        if(ext.lower() == '.pdf'):
            response.render()
            html = response.getvalue()
            html = html.replace(b'/static/', b'file:///betasmartz/static/')
            pdf_builder = HTML(string=html)
            response = HttpResponse(pdf_builder.write_pdf(),
                                    content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="statement_%s.pdf"'%obj.date
        return response



class StatementView(PDFView):
    template_name = "statements/statement_of_advice.html"
    model = StatementOfAdvice
class RecordView(PDFView):
    template_name = "statements/record_of_advice.html"
    model = RecordOfAdvice

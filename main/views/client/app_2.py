__author__ = 'cristian'
from django.views.generic import TemplateView
from ..base import ClientView

__all__ = ["ClientApp2"]


class ClientApp2(TemplateView, ClientView):
    template_name = "client_app/app.html"
    pass

__author__ = 'cristian'
from django.views.generic import TemplateView
from ..base import ClientView
__all__ = ["ClientApp"]


class ClientApp(TemplateView, ClientView):
    template_name = "client-app.html"
    pass

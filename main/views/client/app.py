__author__ = 'cristian'
from django.views.generic import TemplateView

__all__ = ["ClientApp"]


class ClientApp(TemplateView):
    template_name = "client-app.html"

    pass
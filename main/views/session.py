__author__ = 'cristian'
from django.views.generic import TemplateView

__all__ = ["Session"]


class Session(TemplateView):
    template_name = "session.json"
    content_type = "application/json"

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

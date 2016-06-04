from django.views.generic import TemplateView

__all__ = ["ClientAppMissing"]


class ClientAppMissing(TemplateView):
    template_name = "client_app/app_missing.html"

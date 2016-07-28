from django.views.generic import TemplateView


class ClientAppMissing(TemplateView):
    template_name = "client_app/app_missing.html"

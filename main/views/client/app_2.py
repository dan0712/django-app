__author__ = 'cristian'
from django.views.generic import TemplateView
from ..base import ClientView

__all__ = ["ClientApp2"]


class ClientApp2(TemplateView, ClientView):
    template_name = "client_app/app.html"

    def dispatch(self, request, *args, **kwargs):
        response = super(ClientApp2, self).dispatch(request, *args, **kwargs)

        user = request.user
        token = user.get_token();
        response.set_cookie('token', token)

        return response

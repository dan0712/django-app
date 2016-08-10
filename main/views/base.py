from support.models import SupportRequest

__author__ = 'cristian'

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.generic.edit import View

from user.decorators import is_advisor, is_authorized_representative, is_client

__all__ = ["AdvisorView", "ClientView", "AdminView", "LegalView"]


class AdvisorView(View):
    advisor = None

    @method_decorator(is_advisor)
    def dispatch(self, request, *args, **kwargs):
        user = SupportRequest.target_user(request)
        self.advisor = user.advisor
        if request.method == "POST":
            if not self.advisor.is_accepted:
                raise PermissionDenied()

        response = super(AdvisorView, self).dispatch(request, *args, **kwargs)

        if hasattr(response, 'context_data'):
            response.context_data["profile"] = user.advisor
            response.context_data["firm"] = user.advisor.firm
            response.context_data["is_advisor_view"] = True

        return response


class LegalView(View):
    def __init__(self, *args, **kwargs):
        self.firm = None
        super(LegalView, self).__init__(*args, **kwargs)

    @method_decorator(is_authorized_representative)
    def dispatch(self, request, *args, **kwargs):
        user = SupportRequest.target_user(request)
        self.firm = user.authorised_representative.firm
        if request.method == "POST":
            if not user.authorised_representative.is_accepted:
                raise PermissionDenied()

        response = super(LegalView, self).dispatch(request, *args, **kwargs)
        if hasattr(response, 'context_data'):
            response.context_data["profile"] = user.authorised_representative
            response.context_data["firm"] = user.authorised_representative.firm
            response.context_data["is_legal_view"] = True
        return response


class ClientView(View):
    client = None
    is_advisor = None

    @method_decorator(is_client)
    def dispatch(self, request, *args, **kwargs):
        user = SupportRequest.target_user(request)
        self.client = user.client
        self.is_advisor = self.request.session.get("is_advisor", False)

        if request.method == "POST":
            if not self.client.is_accepted:
                raise PermissionDenied()
        return super(ClientView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(ClientView, self).get_context_data(**kwargs)
        user = SupportRequest.target_user(self.request)
        ctx["profile"] = user.client
        ctx["is_advisor"] = "true" if self.request.session.get("is_advisor", False) else "false"
        ctx["is_demo"] = "true" if settings.IS_DEMO else "false"
        return ctx


class AdminView(View):
    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AdminView, self).dispatch(request, *args, **kwargs)

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.generic.base import ContextMixin
from django.views.generic.edit import View

from support.models import SupportRequest
import logging

logger = logging.getLogger('main.views.base')


class AdvisorView(ContextMixin, View):
    advisor = None

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = SupportRequest.target_user(request)
        try:
            self.advisor = user.advisor
        except AttributeError:
            raise PermissionDenied()
        if request.method == "POST" and not self.advisor.is_accepted:
            raise PermissionDenied()

        return super(AdvisorView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        cd = super(AdvisorView, self).get_context_data(**kwargs)
        cd.update({
            "profile": self.advisor,
            "firm": self.advisor.firm,
            "is_advisor_view": True,
        })
        return cd


class LegalView(View):
    def __init__(self, *args, **kwargs):
        self.firm = None
        super(LegalView, self).__init__(*args, **kwargs)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = SupportRequest.target_user(request)
        try:
            self.firm = user.authorised_representative.firm
        except AttributeError:
            PermissionDenied()

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

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = SupportRequest.target_user(request)
        try:
            self.client = user.client
        except AttributeError:
            raise PermissionDenied()

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
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied()
        return super(AdminView, self).dispatch(request, *args, **kwargs)

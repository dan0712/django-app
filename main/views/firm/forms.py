__author__ = 'cristian'

from ..base import AdminView
from django.views.generic import CreateView
from ...models import Firm, INVITATION_LEGAL_REPRESENTATIVE, EmailInvitation
from ...forms import EmailInviteForm
from django.contrib import messages


__all__ = ["InviteLegalView"]

class InviteLegalView(CreateView, AdminView):
    form_class = EmailInviteForm
    template_name = 'admin/betasmartz/legal_invite.html'

    def get_success_url(self):
        messages.info(self.request, "Invite sent successfully!")
        return self.request.get_full_path()

    def dispatch(self, request, *args, **kwargs):
        response = super(InviteLegalView, self).dispatch(request, *args, **kwargs)
        if hasattr(response, 'context_data'):
            firm = Firm.objects.get(pk=kwargs["pk"])
            response.context_data["firm"] = firm
            response.context_data["invitation_type"] = INVITATION_LEGAL_REPRESENTATIVE
            response.context_data["next"] = request.GET.get("next", None)
            response.context_data["invites"] = EmailInvitation.objects.filter(invitation_type=INVITATION_LEGAL_REPRESENTATIVE,
                                                                              inviter_id=firm.pk,
                                                                              inviter_type=firm.content_type,
                                                                              )
        return response
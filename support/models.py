from __future__ import unicode_literals

from django.db import models

from common.constants import PERM_CAN_CREATE_SUPPORT_REQUESTS, \
    KEY_SUPPORT_TICKET


class SupportRequest(models.Model):
    ticket = models.CharField(max_length=30, unique=True)
    user = models.ForeignKey('main.User', related_name='had_support')
    staff = models.ForeignKey('main.User', related_name='gave_support')
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = PERM_CAN_CREATE_SUPPORT_REQUESTS,

    @classmethod
    def target_user(cls, request):
        """
        :rtype: main.User
        """
        user = request.user
        if user.is_authenticated() and user.is_support_staff:
            sr = SupportRequest.get_current(request, as_obj=True)
            if sr:
                user = sr.user
        return user

    @classmethod
    def get_current(cls, request, as_obj=False):
        """
        :rtype: SupportRequest
        """
        try:
            pk = request.session.get(KEY_SUPPORT_TICKET, None)
            if pk is not None:
                if as_obj:
                    # omit `staff` in select_related as it's never used in code
                    return cls.objects.select_related('user').get(pk=pk)
                return pk
        except AttributeError:
            pass

    def set_current(self, request):
        request.session[KEY_SUPPORT_TICKET] = self.id

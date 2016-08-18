from __future__ import unicode_literals

from django.contrib import admin

from common.constants import GROUP_SUPPORT_STAFF
from support.models import SupportRequest


class SupportRequestAdmin(admin.ModelAdmin):
    list_display = 'id', 'ticket', 'user', 'staff'
    fields = 'ticket', 'user'
    list_display_links = 'ticket',
    actions = 'set_current',
    # uncomment when many users and loads slow
    # raw_id_fields = 'user',

    def set_current(self, request, queryset):
        if len(queryset) != 1:
            self.message_user(request, 'You must select one ticket only')
        else:
            queryset[0].set_current(request)
    set_current.short_description = 'Set current'

    def has_module_permission(self, request):
        return request.user.is_support_staff

    def has_add_permission(self, request):
        return request.user.is_support_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_support_staff

    def save_model(self, request, obj: SupportRequest, form, change):
        obj.staff = request.user
        super(SupportRequestAdmin, self).save_model(
            request, obj, form, change
        )
        obj.set_current(request)


admin.site.register(SupportRequest, SupportRequestAdmin)

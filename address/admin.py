from django.conf import settings
from django.contrib import admin
from django.shortcuts import HttpResponseRedirect, render_to_response
from genericadmin.admin import BaseGenericModelAdmin, GenericAdminModelAdmin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Region, Address


class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'country')


class AddressAdmin(admin.ModelAdmin):
    list_display = ('address', 'post_code', 'global_id', 'region')


admin.site.register(Region, RegionAdmin)
admin.site.register(Address, AddressAdmin)

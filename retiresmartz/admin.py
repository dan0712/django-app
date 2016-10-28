from __future__ import unicode_literals

from django.contrib import admin

from main.models import Inflation


class InflationAdmin(admin.ModelAdmin):
    list_display = 'year', 'month', 'value'

admin.site.register(Inflation, InflationAdmin)

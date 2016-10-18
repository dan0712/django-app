from __future__ import unicode_literals

import datetime

from dateutil.relativedelta import relativedelta
from django.contrib import admin, messages
from django.db import transaction
from django.utils.timezone import now

from retiresmartz.models import InflationForecast, InflationForecastImport


class ImportDateFilter(admin.SimpleListFilter):
    title = 'Was imported on'
    parameter_name = 'imported_on'

    def lookups(self, request, model_admin):
        return [
            (o.id, '{0:%Y-%m-%d %H:%M:%S}'.format(o.created_date))
            for o in InflationForecastImport.objects.all()
            ]

    def queryset(self, request, queryset):
        v = self.value()
        if v:
            return queryset.filter(imported=v)


class InflationForecastAdmin(admin.ModelAdmin):
    list_display = 'date', 'value'
    list_filter = ImportDateFilter,


class InflationForecastImportAdmin(admin.ModelAdmin):
    list_display = 'date', 'created_date'

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj: InflationForecastImport, form, change):
        if change:  # cannot change
            self.message_user(request, "Imported record cannot be modified.")
            return
        with transaction.atomic():
            # Get data values from the file
            try:
                data = list(map(float, obj.csv_file.read().split()))
            except (TypeError, ValueError):
                self.message_user(request,
                                  'File cannot be read. Check file format.',
                                  messages.ERROR)
                return
            # load data
            super(InflationForecastImportAdmin, self).save_model(
                request, obj, form, change
            )
            obj.load(obj.date.year, data)


admin.site.register(InflationForecast, InflationForecastAdmin)
admin.site.register(InflationForecastImport, InflationForecastImportAdmin)

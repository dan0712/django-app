from __future__ import unicode_literals

from django.contrib import admin

from retiresmartz.models import RetirementLifestyle


class RetirementLifestyleAdmin(admin.ModelAdmin):
    model = RetirementLifestyle
    list_display = ('cost',)

admin.site.register(RetirementLifestyle, RetirementLifestyleAdmin)

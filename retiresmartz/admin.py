from __future__ import unicode_literals

from django.contrib import admin

from retiresmartz.models import RetirementLifestyle, RetirementAdvice


class RetirementLifestyleAdmin(admin.ModelAdmin):
    model = RetirementLifestyle
    list_display = ('cost',)


class RetirementAdviceAdmin(admin.ModelAdmin):
    model = RetirementAdvice


admin.site.register(RetirementLifestyle, RetirementLifestyleAdmin)
admin.site.register(RetirementAdvice, RetirementAdviceAdmin)

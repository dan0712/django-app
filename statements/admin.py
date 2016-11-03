from __future__ import unicode_literals

from django.contrib import admin

from statements.models import StatementOfAdvice, RetirementStatementOfAdvice


class StatementOfAdviceAdmin(admin.ModelAdmin):
    model = StatementOfAdvice


class RetirementStatementOfAdviceAdmin(admin.ModelAdmin):
    model = RetirementStatementOfAdvice


admin.site.register(StatementOfAdvice, StatementOfAdviceAdmin)
admin.site.register(RetirementStatementOfAdvice, RetirementStatementOfAdviceAdmin)

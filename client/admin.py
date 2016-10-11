from django.contrib import admin
from django.db.models import TextField
from django.forms import Textarea
from nested_admin.nested import NestedModelAdmin, NestedTabularInline

from client.models import (AccountTypeRiskProfileGroup, Client, ClientAccount,
    RiskProfileAnswer, RiskProfileGroup, RiskProfileQuestion)
from main.admin import approve_application


class ClientAccountInline(admin.StackedInline):
    model = ClientAccount


class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_num', 'is_accepted', 'is_confirmed', 'firm')
    list_filter = ('is_accepted',)
    actions = (approve_application,)
    inlines = (ClientAccountInline,)

    def get_queryset(self, request):
        qs = super(ClientAdmin, self).get_queryset(request)
        return qs.filter(user__prepopulated=False)


class ClientAccountAdmin(admin.ModelAdmin):
    pass


class RiskProfileAnswerInline(NestedTabularInline):
    model = RiskProfileAnswer
    sortable_field_name = "order"
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 100})},
    }
    extra = 0


class RiskProfileQuestionInline(NestedTabularInline):
    model = RiskProfileQuestion
    sortable_field_name = "order"
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 100})},
    }
    extra = 0
    inlines = [RiskProfileAnswerInline]


class RiskProfileGroupAdmin(NestedModelAdmin):
    list_display = ('name', 'description',)
    inlines = [RiskProfileQuestionInline]


class AccountTypeRiskProfileGroupAdmin(admin.ModelAdmin):
    list_display = ('account_type', 'risk_profile_group')
    list_editable = ('account_type', 'risk_profile_group')


class RiskProfileQuestionAdmin(admin.ModelAdmin):
    model = RiskProfileQuestion
    list_display = ('text', 'group', 'order')


class RiskProfileAnswerAdmin(admin.ModelAdmin):
    model = RiskProfileAnswer
    list_display = ('text', 'question', 'order')


admin.site.register(Client, ClientAdmin)
admin.site.register(ClientAccount, ClientAccountAdmin)
admin.site.register(RiskProfileGroup, RiskProfileGroupAdmin)
admin.site.register(AccountTypeRiskProfileGroup,
                    AccountTypeRiskProfileGroupAdmin)
admin.site.register(RiskProfileQuestion, RiskProfileQuestionAdmin)
admin.site.register(RiskProfileAnswer, RiskProfileAnswerAdmin)

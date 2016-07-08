from django.db.models.fields import TextField
from django.forms.widgets import Textarea
from genericadmin.admin import GenericAdminModelAdmin, BaseGenericModelAdmin
import nested_admin

from advisors import models as advisor_models
from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.shortcuts import render_to_response, HttpResponseRedirect
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from main.models import (
    Firm, Advisor, User, Performer,
    AuthorisedRepresentative, FirmData, Client, ClientAccount,
    Goal, GoalMetric, GoalSetting, Position, Transaction,
    EventMemo, Dividend,
    ProxyAssetClass, ProxyTicker, PortfolioSet,
    Portfolio, PortfolioItem, View,
    GoalType, GoalMetricGroup, MarketIndex, RiskProfileGroup, RiskProfileQuestion, RiskProfileAnswer, ActivityLog,
    ActivityLogEvent, DailyPrice,
    MarketOrderRequest, Execution, ExecutionDistribution, Ticker, # These are activated at the bottom
    AccountTypeRiskProfileGroup)

from suit.admin import SortableModelAdmin, SortableTabularInline


from main.models import AccountGroup
admin.site.register(AccountGroup)


class AssetResource(resources.ModelResource):
    class Meta:
        model = ProxyAssetClass


class TickerInline(BaseGenericModelAdmin, SortableTabularInline):
    model = ProxyTicker
    sortable = 'ordering'
    extra = 0
    generic_fk_fields = [{
        'ct_field': 'benchmark_content_type',
        'fk_field': 'benchmark_object_id',
    }]


class DailyPriceAdmin(GenericAdminModelAdmin):
    model = DailyPrice
    list_display = ('date', 'price', 'instrument_content_type', 'instrument_object_id')
    #sortable = 'date'
    #extra = 0
    generic_fk_fields = [{
        'ct_field': 'instrument_content_type',
        'fk_field': 'instrument_object_id',
    }]
    list_editable = ('date', 'price', 'instrument_content_type', 'instrument_object_id')


class ClientAccountInline(admin.StackedInline):
    model = ClientAccount


class EventMemoInline(admin.StackedInline):
    model = EventMemo
    extra = 0


class PortfolioViewsInline(admin.StackedInline):
    model = View
    extra = 0


class AdvisorInline(admin.StackedInline):
    model = Advisor


class AuthorisedRepresentativeInline(admin.StackedInline):
    model = AuthorisedRepresentative


class FirmDataInline(admin.StackedInline):
    model = FirmData


class AssetClassAdmin(GenericAdminModelAdmin, SortableModelAdmin, ImportExportModelAdmin):
    list_display = ('name', 'display_name', 'display_order', 'investment_type', 'super_asset_class')
    inlines = (TickerInline,)
    resource_class = AssetResource
    sortable = 'display_order'


class FirmFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'filter by firm'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'firm'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        list_id = [[None, "All"]]
        for firm in Firm.objects.all():
            list_id.append([firm.pk, firm.name])

        return list_id

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or 'other')
        # to decide how to filter the queryset.

        if self.value() is None:
            return queryset.all()

        return queryset.filter(firm__pk=self.value())


def approve_application(modeladmin, request, queryset):
    for obj in queryset.all():
        obj.approve()


approve_application.short_description = "Approve application(s)"


class AdvisorAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_num', 'is_accepted', 'is_confirmed', 'firm')
    list_filter = ('is_accepted', FirmFilter)
    actions = (approve_application,)

    pass


class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_num', 'is_accepted', 'is_confirmed', 'firm')
    list_filter = ('is_accepted',)
    actions = (approve_application,)
    inlines = (ClientAccountInline,)

    def get_queryset(self, request):
        qs = super(ClientAdmin, self).get_queryset(request)
        return qs.filter(user__prepopulated=False)


class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email')

    def get_form(self, request, obj=None, **kwargs):
        form = super(UserAdmin, self).get_form(request, obj, **kwargs)

        def clean_password(me):
            password = me.cleaned_data['password']

            if me.instance:
                if me.instance.password != password:
                    password = make_password(password)
            else:
                password = make_password(password)

            print(password, "*******************")
            return password

        form.clean_password = clean_password

        return form

    pass


def rebalance(modeladmin, request, queryset):
    context = {'STATIC_URL': settings.STATIC_URL, 'MEDIA_URL': settings.MEDIA_URL, 'item_class': 'transaction'}

    if queryset.count() > 1:
        return render_to_response('admin/betasmartz/error_only_one_item.html', context)

    else:
        return HttpResponseRedirect('/betasmartz_admin/rebalance/{pk}?next=/admin/main/firm/'
                                    .format(pk=queryset.all()[0].pk))


def execute_transaction(modeladmin, request, queryset):
    context = {'STATIC_URL': settings.STATIC_URL, 'MEDIA_URL': settings.MEDIA_URL, 'item_class': 'transaction'}

    if queryset.count() > 1:
        return render_to_response('admin/betasmartz/error_only_one_item.html', context)

    else:
        return HttpResponseRedirect('/betasmartz_admin/transaction/{pk}/execute?next=/admin/main/firm/'
                                    .format(pk=queryset.all()[0].pk))


def invite_authorised_representative(modeladmin, request, queryset):
    context = {'STATIC_URL': settings.STATIC_URL, 'MEDIA_URL': settings.MEDIA_URL, 'item_class': 'firm'}

    if queryset.count() > 1:
        return render_to_response('admin/betasmartz/error_only_one_item.html', context)

    else:
        return HttpResponseRedirect('/betasmartz_admin/firm/{pk}/invite_legal?next=/admin/main/firm/'
                                    .format(pk=queryset.all()[0].pk))


def invite_advisor(modeladmin, request, queryset):
    context = {'STATIC_URL': settings.STATIC_URL, 'MEDIA_URL': settings.MEDIA_URL, 'item_class': 'firm'}

    if queryset.count() > 1:
        return render_to_response('admin/betasmartz/error_only_one_item.html', context)

    else:
        return HttpResponseRedirect('/betasmartz_admin/firm/{pk}/invite_advisor?next=/admin/main/firm/'
                                    .format(pk=queryset.all()[0].pk))


def invite_supervisor(modeladmin, request, queryset):
    context = {'STATIC_URL': settings.STATIC_URL, 'MEDIA_URL': settings.MEDIA_URL, 'item_class': 'firm'}

    if queryset.count() > 1:
        return render_to_response('admin/betasmartz/error_only_one_item.html', context)

    else:
        return HttpResponseRedirect('/betasmartz_admin/firm/{pk}/invite_supervisor?next=/admin/main/firm/'
                                    .format(pk=queryset.all()[0].pk))


class FirmAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = (FirmDataInline,)
    actions = (invite_authorised_representative, invite_advisor, invite_supervisor)


class AuthorisedRepresentativeAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_num', 'is_accepted', 'is_confirmed', 'firm')
    list_filter = ('is_accepted', FirmFilter)
    actions = (approve_application,)


class ClientAccountAdmin(admin.ModelAdmin):
    pass


class GoalMetricInline(admin.StackedInline):
    model = GoalMetric


class GoalMetricGroupAdmin(admin.ModelAdmin):
    model = GoalMetricGroup
    inlines = (GoalMetricInline,)


class GoalSettingAdmin(admin.ModelAdmin):
    model = GoalSetting


class GoalTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'default_term', 'risk_sensitivity', 'order')
    list_editable = ('group', 'default_term', 'risk_sensitivity', 'order')


class AccountTypeRiskProfileGroupAdmin(admin.ModelAdmin):
    list_display = ('account_type', 'risk_profile_group')
    list_editable = ('account_type', 'risk_profile_group')


class GoalAdmin(admin.ModelAdmin):
    list_display = ('account', 'name', 'type')
    actions = (rebalance,)


class PositionAdmin(admin.ModelAdmin):
    list_display = ('goal', 'ticker', 'value')


class PortfolioItemInline(admin.StackedInline):
    model = PortfolioItem


class PortfolioAdmin(admin.ModelAdmin):
    inlines = (PortfolioItemInline,)


class PortfolioSetAdmin(admin.ModelAdmin):
    filter_horizontal = ('asset_classes',)
    inlines = (PortfolioViewsInline,)


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('reason', 'from_goal', 'to_goal', 'status', 'amount', 'created')
    actions = (execute_transaction,)
    list_filter = ('status',)


class PerformerAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'group', 'allocation')


def approve_changes(modeladmin, request, queryset):
    for obj in queryset.all():
        obj.approve()
    messages.info(request, "Changes have been approved and applied")


class AdvisorChangeDealerGroupAdmin(admin.ModelAdmin):
    list_display = ('advisor', 'new_email', 'old_firm', 'new_firm', 'approved', 'create_at', 'approved_at')
    list_filter = ('advisor', 'old_firm', 'new_firm', 'approved')
    actions = (approve_changes,)


class AdvisorBulkInvestorTransferAdmin(admin.ModelAdmin):
    filter_horizontal = ('investors',)
    list_display = ('from_advisor', 'to_advisor', 'approved', 'create_at', 'approved_at')
    list_filter = ('from_advisor', 'to_advisor', 'approved')
    actions = (approve_changes,)


class AdvisorSingleInvestorTransferAdmin(admin.ModelAdmin):
    list_display = ('from_advisor', 'to_advisor', 'firm', 'investor', 'approved', 'create_at', 'approved_at')
    list_filter = ('from_advisor', 'to_advisor', 'investor', 'approved')
    actions = (approve_changes,)


class RiskProfileAnswerInline(nested_admin.NestedTabularInline):
    model = RiskProfileAnswer
    sortable_field_name = "order"
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 100})},
    }
    extra = 0


class RiskProfileQuestionInline(nested_admin.NestedTabularInline):
    model = RiskProfileQuestion
    sortable_field_name = "order"
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 100})},
    }
    extra = 0
    inlines = [RiskProfileAnswerInline]


class RiskProfileGroupAdmin(nested_admin.NestedModelAdmin):
    list_display = ('name', 'description',)
    inlines = [RiskProfileQuestionInline]


class ActivityLogEventAdminInline(admin.TabularInline):
    model = ActivityLogEvent


class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('name', 'format_str', 'format_args')
    list_editable = ('name', 'format_str', 'format_args')
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 100})},
    }
    inlines = (ActivityLogEventAdminInline,)


admin.site.register(advisor_models.ChangeDealerGroup, AdvisorChangeDealerGroupAdmin)
admin.site.register(advisor_models.SingleInvestorTransfer, AdvisorSingleInvestorTransferAdmin)
admin.site.register(advisor_models.BulkInvestorTransfer, AdvisorBulkInvestorTransferAdmin)
admin.site.register(Performer, PerformerAdmin)
admin.site.register(ClientAccount, ClientAccountAdmin)
admin.site.register(Goal, GoalAdmin)
admin.site.register(GoalType, GoalTypeAdmin)
admin.site.register(MarketIndex)
admin.site.register(GoalSetting, GoalSettingAdmin)
admin.site.register(GoalMetricGroup, GoalMetricGroupAdmin)
admin.site.register(Dividend)
admin.site.register(ProxyAssetClass, AssetClassAdmin)
admin.site.register(Firm, FirmAdmin)
admin.site.register(Advisor, AdvisorAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(AuthorisedRepresentative, AuthorisedRepresentativeAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Portfolio, PortfolioAdmin)
admin.site.register(PortfolioSet, PortfolioSetAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(RiskProfileGroup, RiskProfileGroupAdmin)
admin.site.register(AccountTypeRiskProfileGroup, AccountTypeRiskProfileGroupAdmin)
admin.site.register(ActivityLog, ActivityLogAdmin)
# The below are commented as non-devs should not be editing them.
# admin.site.register(DailyPrice, DailyPriceAdmin)
# admin.site.register(MarketOrderRequest)
# admin.site.register(Execution)
# admin.site.register(ExecutionDistribution)
# admin.site.register(Ticker)
# End non-dev section
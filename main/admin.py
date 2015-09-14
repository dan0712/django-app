__author__ = 'cristian'

from django.contrib import admin
from portfolios.models import ProxyAssetClass, ProxyTicker, PortfolioSet, View, PortfolioByRisk
from main.models import Firm, Advisor, User, AUTHORIZED_REPRESENTATIVE, \
    AuthorisedRepresentative, FirmData, Client, ClientAccount, Goal, Platform, Position, Transaction, TransactionMemo
from suit.admin import SortableTabularInline
from suit.admin import SortableModelAdmin
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.hashers import make_password


class TickerInline(SortableTabularInline):
    model = ProxyTicker
    sortable = 'ordering'
    extra = 0


class ClientAccountInline(admin.StackedInline):
    model = ClientAccount


class TransactionMemoInline(admin.StackedInline):
    model = TransactionMemo
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


class AssetClassAdmin(SortableModelAdmin):
    list_display = ('name', 'display_name', 'display_order', 'investment_type', 'super_asset_class')
    inlines = (TickerInline,)
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
    list_display = ('user', 'phone_number', 'is_accepted', 'is_confirmed', 'firm')
    list_filter = ('is_accepted', FirmFilter)
    actions = (approve_application, )

    pass


class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'is_accepted', 'is_confirmed', 'firm')
    list_filter = ('is_accepted', )
    actions = (approve_application, )
    inlines = (ClientAccountInline, )
    pass


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
    list_display = ('name', )
    inlines = (FirmDataInline, )
    actions = (invite_authorised_representative, invite_advisor, invite_supervisor)


class AuthorisedRepresentativeAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'is_accepted', 'is_confirmed', 'firm')
    list_filter = ('is_accepted', FirmFilter)
    actions = (approve_application, )

    pass


class ClientAccountAdmin(admin.ModelAdmin):
    pass


class GoalAdmin(admin.ModelAdmin):
    list_display = ('account', 'name', 'total_balance_db', 'allocation', 'drift', 'type')
    actions = (rebalance, )
    pass


class PlatformAdminAdmin(admin.ModelAdmin):
    pass


class PositionAdmin(admin.ModelAdmin):
    list_display = ('goal', 'ticker', 'value')
    pass


class PortfolioSetAdmin(admin.ModelAdmin):
    filter_horizontal = ('asset_classes',)
    inlines = (PortfolioViewsInline, )
    pass


class PortfolioByRiskAdmin(admin.ModelAdmin):
    list_display = ('risk', 'portfolio_set', 'expected_return', 'volatility')
    pass

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('account', 'type', 'from_account', 'to_account', 'status', 'amount', 'created_date')
    inlines = (TransactionMemoInline,)
    actions = (execute_transaction, )
    list_filter = ('status', )

admin.site.register(PortfolioByRisk, PortfolioByRiskAdmin)

admin.site.register(Platform, PlatformAdminAdmin)
admin.site.register(ClientAccount, ClientAccountAdmin)
admin.site.register(Goal, GoalAdmin)

admin.site.register(ProxyAssetClass, AssetClassAdmin)
admin.site.register(Firm, FirmAdmin)
admin.site.register(Advisor, AdvisorAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(AuthorisedRepresentative, AuthorisedRepresentativeAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(PortfolioSet, PortfolioSetAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Transaction, TransactionAdmin)
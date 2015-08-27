__author__ = 'cristian'

from django.contrib import admin
from portfolios.models import ProxyAssetClass, ProxyTicker
from main.models import Firm, Advisor, User
from suit.admin import SortableTabularInline
from suit.admin import SortableModelAdmin


class TickerInline(SortableTabularInline):
    model = ProxyTicker
    sortable = 'ordering'


class AdvisorInline(admin.StackedInline):
    model = Advisor


class AssetClassAdmin(SortableModelAdmin):
    list_display = ('name', 'display_name', 'display_order', 'investment_type', 'super_asset_class')
    inlines = (TickerInline,)
    sortable = 'display_order'


class AdvisorAdmin(admin.ModelAdmin):
    list_display = ('user', 'work_phone', 'is_accepted', 'is_confirmed', 'is_supervisor', 'firm')
    pass


class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email')
    pass


class FirmAdmin(admin.ModelAdmin):
    list_display = ('firm_name', )
    inlines = (AdvisorInline,)
    pass

admin.site.register(ProxyAssetClass, AssetClassAdmin)
admin.site.register(Firm, FirmAdmin)
admin.site.register(Advisor, AdvisorAdmin)
admin.site.register(User, UserAdmin)
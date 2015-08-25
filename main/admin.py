__author__ = 'cristian'

from django.contrib import admin
from portfolios.models import ProxyAssetClass, ProxyTicker
from suit.admin import SortableTabularInline
from suit.admin import SortableModelAdmin


class CountryInline(SortableTabularInline):
    model = ProxyTicker
    sortable = 'ordering'


class AssetClassAdmin(SortableModelAdmin):
    list_display = ('name', 'display_name', 'display_order', 'investment_type', 'super_asset_class')
    inlines = (CountryInline,)
    sortable = 'display_order'


admin.site.register(ProxyAssetClass, AssetClassAdmin)
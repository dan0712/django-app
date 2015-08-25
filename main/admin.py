__author__ = 'cristian'

from django.contrib import admin
from portfolios.models import ProxyAssetClass, ProxyTicker
from suit.admin import SortableTabularInline


class CountryInline(SortableTabularInline):
    model = ProxyTicker
    sortable = 'ordering'


class AssetClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_order', 'donut_order', 'investment_type', 'super_asset_class')
    inlines = (CountryInline,)
    pass

admin.site.register(ProxyAssetClass, AssetClassAdmin)


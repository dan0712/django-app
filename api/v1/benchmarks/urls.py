from __future__ import unicode_literals

from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(r'^$', views.AvailableListView.as_view(), name='list'),
    url(r'^(?P<pk>\d+)/returns/?$', views.ReturnsView.as_view(), name='single'),
)

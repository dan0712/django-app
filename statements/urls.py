from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = patterns(
    '',
    url(r'^records/(?P<pk>\d+)(?P<ext>(\.pdf)?)$', views.RecordView.as_view(), name='record_of_advice'),
    url(r'^(?P<pk>\d+)(?P<ext>(\.\w{3})?)$', views.StatementView.as_view(), name='statement_of_advice'),
)

from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from main.views import ClientAppMissing

app_view = login_required(ClientAppMissing.as_view())
urlpatterns = patterns(
    '',
    # The React code should pick up this route.
    # If it doesn't, there is a configuration problem.
    url(r'^(?P<pk>\d+)/account/(?P<account_id>\d+)$', app_view, name='account'),
    url(r'^(?P<pk>\d+)$', app_view, name='app'),
)

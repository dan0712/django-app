from django.conf.urls import patterns, include, url
from api.v1.client.views import *

urlpatterns = patterns('',

                       (r'^api/v1/client/?$', APIClient.as_view()),

                       (r'^api/v1/client/accounts/?$', APIClientAccounts.as_view()),
)

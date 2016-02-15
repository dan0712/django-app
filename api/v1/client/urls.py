from django.conf.urls import patterns, include, url
from api.v1.client.views import *

urlpatterns = patterns('',
   (r'^client/?$', APIClient.as_view()),
   (r'^client/accounts/?$', APIClientAccounts.as_view()),
)

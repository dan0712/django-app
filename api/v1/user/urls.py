from django.conf.urls import patterns, include, url
from api.v1.user.views import *

import api.v1.user.views as views


urlpatterns = patterns('',
    url(r'^user/?$', APIUser.as_view(), name='user'), # TODO: bearly needed
    url(r'^user/level/?$', APIUserLevel.as_view(), name='user-level'), # TODO: lets drop it

    url(r'^me/?$', views.MeView.as_view(), name='user-me'),
    url(r'^login/?$', views.LoginView.as_view(), name='user-login'),
    # reserved # url(r'^register/$', views.RegisterView.as_view(), name='user-register'),

    # reserved # url(r'^register/reset/$', views.ResetView.as_view(), name='user-reset'),
    # reserved # url(r'^register/send-reset-email/$', views.SendResetEmailView.as_view(), name='user-send-reset-email'),
)

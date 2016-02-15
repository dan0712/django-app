from django.conf.urls import patterns, include, url
from api.v1.user.views import *

import api.v1.user.views as views


urlpatterns = patterns('',
    (r'^user/?$', APIUser.as_view()), # TODO: bearly needed
    (r'^user/level/?$', APIUserLevel.as_view()), # TODO: lets drop it

    (r'^me/$', views.MeView.as_view()),
    (r'^signin/$', views.SigninView.as_view()),
    # reserved # (r'^signup/$', views.SigninView.as_view()),

    # reserved # (r'^signin/reset/$', views.ResetView.as_view(), name='auth-reset'),
    # reserved # (r'^signin/send-reset-email/$', views.SendResetEmailView.as_view(), name='auth-send-reset-email'),
)

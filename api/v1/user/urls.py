from django.conf.urls import patterns, include, url
from api.v1.user.views import *

urlpatterns = patterns('',

                       (r'^api/v1/user/?$', APIUser.as_view()),
                       (r'^api/v1/user/level/?$', APIUserLevel.as_view()),

)

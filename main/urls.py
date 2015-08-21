from django.conf.urls import patterns, include, url
from django.contrib import admin
from .views import *

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'main.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    # Advisor views
    url(r'^advisor/login', advisor_login, name='advisor:login'),

    # Client views
    url(r'^client/login', client_login, name='client:login'),

)

from __future__ import unicode_literals

from django.conf.urls import patterns, url

from main import views as main_views
from . import views

urlpatterns = patterns(
    '',

    url(r'^$', views.AdvisorClients.as_view(), name='list'),
    url(r'^(?P<pk>\d+)$', views.AdvisorClientDetails.as_view(),
        name='detail'),
    url(r'^(?P<pk>\d+)/account-invites$',
        views.AdvisorCreateNewAccountForExistingClient.as_view(),
        name='account-invites'),

    url(r'^(?P<pk>\d+)/account-invites/create$',
        views.AdvisorCreateNewAccountForExistingClientSelectAccountType.as_view(),
        name='account-invites-create'),

    url(r'^invites$', views.AdvisorClientInvites.as_view(), name='invites'),
    url(r'^invites/new$', views.AdvisorNewClientInviteView.as_view(), name='invites-new'),

    url(r'^invites/create$', main_views.AdvisorClientInviteNewView.as_view(),
        name='invites-create'),
    url(r'^invites/create/profile$',
        main_views.CreateNewClientPrepopulatedView.as_view(),
        name='invites-create-profile'),
    url(r'^invites/(?P<pk>\d+)/create/personal-details$',
        main_views.BuildPersonalDetails.as_view(),
        name='invites-create-personal-details'),
    url(r'^invites/(?P<pk>\d+)/create/financial-details$',
        main_views.BuildFinancialDetails.as_view(),
        name='invites-create-financial-details'),
    url(r'^invites/(?P<pk>\d+)/create/confirm$',
        main_views.BuildConfirm.as_view(), name='invites-create-confirm'),

)

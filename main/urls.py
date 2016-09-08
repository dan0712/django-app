from django.conf.urls import include, patterns, url
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from filebrowser.sites import site

from api.v1.user.views import PasswordResetView
from main import settings
from main.views import *
from main.views.client.app_missing import ClientAppMissing


def ok_response_json(*args, **kwargs):
    return HttpResponse("[]", content_type='application/json')

# TODO: modularize later
urlpatterns_firm = patterns(
    '',
    url(r'^overview$', FirmOverview.as_view(), name='overview'),
    url(r'^analytics$', FirmAnalyticsOverviewView.as_view(), name='analytics'), # aka 'analytics-overview'
    url(r'^analytics/metric$', FirmAnalyticsOverviewMetricView.as_view(), name='analytics-overview-metric'),
    url(r'^analytics/advisors$', FirmAnalyticsAdvisorsView.as_view(), name='analytics-advisors'),
    url(r'^analytics/advisors/(?P<pk>\d+)$', FirmAnalyticsAdvisorsDetailView.as_view(), name='analytics-advisors-detail'),
    url(r'^analytics/clients$', FirmAnalyticsClientsView.as_view(), name='analytics-clients'),
    url(r'^analytics/clients/(?P<pk>\d+)$', FirmAnalyticsClientsDetailView.as_view(), name='analytics-clients-detail'),

    url(r'^activity$', FirmActivityView.as_view(), name='activity'),
    url(r'^application$', FirmApplicationView.as_view(), name='application'),
    url(r'^support$', FirmSupport.as_view(), name='support'),
    url(r'^support/forms$', FirmSupportForms.as_view(), name='support-forms'),
    url(r'^support/pricing$', FirmSupportPricingView.as_view(), name='support-pricing'),

    # url(r'^advisor_invites', FirmAdvisorInvites.as_view()), # TODO: revamp
    # url(r'^supervisor_invites', FirmSupervisorInvites.as_view()), # TODO: revamp

    url(r'^edit$', FirmDataView.as_view(), name='edit'), # TODO: revamp

    url(r'^overview/advisors/(?P<pk>\d+)$', FirmAdvisorAccountOverview.as_view(), name='overview-advisor'),
    url(r'^overview/advisors/(?P<pk>\d+)/clients$', FirmAdvisorClients.as_view(), name='overview-advisor-clients'),
    url(r'^overview/advisors/(?P<pk>\d+)/client/(?P<client_id>\d+)$', FirmAdvisorClientDetails.as_view(), name='overview-advisor-clients-detail'),

    # OBSOLETED # url(r'^agreements$', FirmAgreements.as_view()),

    url(r'^supervisors$', FirmSupervisors.as_view(), name='supervisors'),
    url(r'^supervisors/create$', FirmSupervisorsCreate.as_view(), name='supervisors-create'),
    url(r'^supervisors/(?P<pk>\d+)/edit', FirmSupervisorsEdit.as_view(), name='supervisors-edit'),
    url(r'^supervisors/(?P<pk>\d+)/delete', FirmSupervisorDelete.as_view(), name='supervisors-delete'),
)

urlpatterns = patterns(
    '',
    url(r'^api/', include('api.urls', namespace='api')),
    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^admin/filebrowser/', include(site.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^nested_admin/', include('nested_admin.urls')),  # For nested stackable admin
    url(r'^support/', include('pages.urls')),

    # Firm views
    url(r'^firm/', include(urlpatterns_firm, namespace='firm')),
    # Client views
    url(r'^client/', include('client.urls', namespace='client', app_name='client')),
    # Client statements
    url(r'^statements/', include('statements.urls', namespace='statements', app_name='statements')),
    # Advisor views
    url(r'^advisor/', include('advisors.urls', namespace='advisor', app_name='advisors')),

    url(r'^session',
        csrf_exempt(Session.as_view()),
        name="session"),
    url(r'^betasmartz_admin/firm/(?P<pk>\d+)/invite_legal',
        InviteLegalView.as_view(),
        name='betasmartz_admin:invite_legal'),
    url(r'^betasmartz_admin/firm/(?P<pk>\d+)/invite_advisor',
        AdminInviteAdvisorView.as_view(),
        name='betasmartz_admin:invite_advisor'),
    url(r'^betasmartz_admin/firm/(?P<pk>\d+)/invite_supervisor',
        AdminInviteSupervisorView.as_view(),
        name='betasmartz_admin:invite_supervisor'),
    url(r'^betasmartz_admin/transaction/(?P<pk>\d+)/execute',
        AdminExecuteTransaction.as_view()),

    url(r'^$', lambda x: HttpResponseRedirect(reverse_lazy('login'))),

    url(r'^login$', login, name='login'),
    url(r'^logout$', logout, name='logout'),
    url(r'^(?P<token>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/legal_signup$',
        AuthorisedRepresentativeSignUp.as_view(),
        name='representative_signup'),
    url(r'^(?P<token>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/advisor_signup',
        AdvisorSignUpView.as_view()),
    url(r'^confirm_email/(?P<type>\d+)/(?P<token>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',
        EmailConfirmationView.as_view()),
    url(r'^confirmation$', Confirmation.as_view(), name='confirmation'),

    url(r'^betasmartz_admin/rebalance/(?P<pk>\d+)$', GoalRebalance.as_view()),

    url(r'^password/reset/$', PasswordResetView.as_view(), name='password_reset'),
    url(r'^password/reset/done/$',
        'django.contrib.auth.views.password_reset_done', name='password_reset_done'),
    url(r'^password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'django.contrib.auth.views.password_reset_confirm',
        {'post_reset_redirect': '/login'},
        name='password_reset_confirm'),

    #url(r'^client/2.0/api/',  include(router.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT,
          'show_indexes': True}),
        url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')), )

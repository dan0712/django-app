from django.conf.urls import patterns, include, url
from django.contrib import admin
from .views import *
from django.views.decorators.csrf import csrf_exempt
from main import  settings

urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),
    url(r'^session', csrf_exempt(Session.as_view()), name="session"),
    url(r'^betasmartz_admin/firm/(?P<pk>\d+)/invite_legal',
        InviteLegalView.as_view(), name='betasmartz_admin:invite_legal'),
    # firm views
    url(r'^(?P<token>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/legal_signup$',
        LegalRepresentativeSignUp.as_view(), name='firm:representative_signup'),

    url(r'^firm/login', firm_login),
    url(r'^firm/sign_out', firm_logout),

    url(r'^firm/advisor_invites', FirmAdvisorInvites.as_view()),
    url(r'^firm/supervisor_invites', FirmSupervisorInvites.as_view()),

    url(r'^firm/support$', FirmSupport.as_view()),
    url(r'^firm/support/forms$', FirmSupportForms.as_view()),
    url(r'^firm/summary',  FirmSummary.as_view()),
    url(r'^firm/change-details$',  FirmDataView.as_view()),


    # Advisor views
    url(r'^advisor/signup', AdvisorSignUpView.as_view(), name='advisor:sign_up'),
    url(r'^advisor/confirm_email/(?P<token>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        AdvisorConfirmEmail.as_view(), name='advisor:confirm_email'),

    url(r'^advisor/client_invites', AdvisorClientInvites.as_view(), name='advisor:client_invites'),
    url(r'^advisor/clients', AdvisorClients.as_view(), name='advisor:clients'),
    url(r'^advisor/agreements', AdvisorAgreements.as_view(), name='advisor:agreements'),
    url(r'^advisor/support', AdvisorSupport.as_view(), name='advisor:support'),
    url(r'^advisor/summary', AdvisorSummary.as_view(), name='advisor:summary'),


    # Client views
    url(r'^client/login', client_login, name='client:login'),
    url(r'^client/app', ClientApp.as_view(), name='client:app'),
    url(r'^(?P<slug>[\w-]+)/client/signup/(?P<token>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        ClientSignUp.as_view(), name='client:sign_up'),

    url(r'^client/api/appData', ClientAppData.as_view(), name='client:api:app_data'),
    url(r'^client/api/asset-classes', ClientAssetClasses.as_view(), name='client:api:asset_classes'),
    url(r'^client/api/user', ClientUserInfo.as_view(), name='client:api:user'),
    url(r'^client/api/visitor', ClientVisitor.as_view(), name='client:api:visitor'),
    url(r'^client/api/advisors/(?P<pk>\d+)', ClientAdvisor.as_view(), name='client:api:advisors'),
    url(r'^client/api/advisors$', ClientAdvisor.as_view(), name='client:api:advisors_2'),

    url(r'^client/api/accounts$', ClientAccounts.as_view(), name='client:api:accounts'),
    url(r'^client/api/firms', ClientFirm.as_view(), name='client:api:firms'),
    url(r'^client/api/accounts/(?P<pk>\d+)/positions', ClientAccountPositions.as_view(),
        name='client:api:accounts:positions'),

    url(r'^client/api/portfolio-sets/(?P<pk>\d+)/asset-classes', PortfolioAssetClasses.as_view(),
        name='client:api:portfolio_sets:asset_classes'),
    url(r'^client/api/portfolio-sets/(?P<pk>\d+)/portfolios', PortfolioPortfolios.as_view(),
        name='client:api:portfolio_sets:portfolios'),
    url(r'^client/api/portfolio-sets/(?P<pk>\d+)/risk-free-rates', PortfolioRiskFreeRates.as_view(),
        name='client:api:portfolio_sets:risk_free_rates'),



)

if settings.DEBUG:
    urlpatterns += patterns('',
                            (r'^media/(?P<path>.*)$', 'django.views.static.serve',
                             {'document_root': settings.MEDIA_ROOT,
                              'show_indexes': True}), )

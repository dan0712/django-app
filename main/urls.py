from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from filebrowser.sites import site
from main import settings
from .views import *


def ok_response_json(*args, **kwargs):
    return HttpResponse("[]", content_type='application/json')

# TODO: modularize later
urlpatterns_firm = patterns(
    '',
    url(r'^summary$', FirmSummary.as_view(), name='summary'),
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

    url(r'^advisor_invites', FirmAdvisorInvites.as_view()), # TODO: revamp
    url(r'^supervisor_invites', FirmSupervisorInvites.as_view()), # TODO: revamp

    url(r'^edit$', FirmDataView.as_view(), name='edit'), # TODO: revamp

    url(r'^summary/advisors/(?P<pk>\d+)$', FirmAdvisorAccountSummary.as_view(), name='summary-advisor'),
    url(r'^summary/advisors/(?P<pk>\d+)/clients$', FirmAdvisorClients.as_view(), name='summary-advisor-clients'),
    url(r'^summary/advisors/(?P<pk>\d+)/client/(?P<client_id>\d+)$', FirmAdvisorClientDetails.as_view(), name='summary-advisor-clients-detail'),

    # OBSOLETED # url(r'^agreements$', FirmAgreements.as_view()),

    url(r'^supervisors$', FirmSupervisors.as_view(), name='supervisors'),
    url(r'^supervisors/create$', FirmSupervisorsCreate.as_view(), name='supervisors-create'),
    url(r'^supervisors/(?P<pk>\d+)/edit', FirmSupervisorsEdit.as_view(), name='supervisors-edit'),
    url(r'^supervisors/(?P<pk>\d+)/delete', FirmSupervisorDelete.as_view(), name='supervisors-delete'),
)

# TODO: modularize later
urlpatterns_advisor = patterns(
    '',
    url(r'^clients$', AdvisorClients.as_view(), name='clients'),
    url(r'^clients/(?P<pk>\d+)$', AdvisorClientDetails.as_view(), name='clients-detail'),
    url(r'^clients/(?P<pk>\d+)/account-invites$', AdvisorCreateNewAccountForExistingClient.as_view(), name='clients-account-invites'),
    url(r'^clients/(?P<pk>\d+)/account-invites/create$', AdvisorCreateNewAccountForExistingClientSelectAccountType.as_view(), name='clients-account-invites-create'),
    url(r'^clients/invites$', AdvisorClientInvites.as_view(), name='clients-invites'),
    url(r'^clients/invites/create$', AdvisorClientInviteNewView.as_view(), name='clients-invites-create'),
    url(r'^clients/invites/create/profile$', CreateNewClientPrepopulatedView.as_view(), name='clients-invites-create-profile'),
    url(r'^clients/invites/(?P<pk>\d+)/create/personal-details$', BuildPersonalDetails.as_view(), name='clients-invites-create-personal-details'),
    url(r'^clients/invites/(?P<pk>\d+)/create/financial-details$', BuildFinancialDetails.as_view(), name='clients-invites-create-financial-details'),
    url(r'^clients/invites/(?P<pk>\d+)/create/confirm$', BuildConfirm.as_view(), name='clients-invites-create-confirm'),

    url(r'^composites/create$', AdvisorCompositeNew.as_view(), name='composites-create'),
    url(r'^composites/(?P<pk>\d+)$', AdvisorAccountGroupDetails.as_view(), name='composites-detail'),
    url(r'^composites/(?P<pk>\d+)/edit$', AdvisorCompositeEdit.as_view(), name='composites-edit'),
    url(r'^composites/(?P<account_id>\d+)/account-groups/(?P<account_group_id>\d+)$',
        AdvisorRemoveAccountFromGroupView.as_view(), name='composites-detail-account-groups-delete'),
    url(r'^composites/(?P<pk>\d+)/clients$',
        AdvisorAccountGroupClients.as_view(), name='composites-detail-clients'),
    url(r'^composites/(?P<pk>\d+)/secondary-advisors$',
        AdvisorAccountGroupSecondaryDetailView.as_view(), name='composites-detail-secondary-advisors'),
    url(r'^composites/(?P<pk>\d+)/secondary-advisors/create$',
        AdvisorAccountGroupSecondaryCreateView.as_view(), name='composites-detail-secondary-advisors-create'),
    url(r'^composites/(?P<pk>\d+)/secondary-advisors/(?P<sa_pk>\d+)$',
        AdvisorAccountGroupSecondaryDeleteView.as_view(), name='composites-detail-secondary-advisors-delete'),
    url(r'^composites/client-accounts/(?P<pk>\d+)/fee$',
        AdvisorClientAccountChangeFee.as_view(), name='composites-client-accounts-fee'),

    url(r'^agreements', AdvisorAgreements.as_view(), name='agreements'),
    url(r'^support$', AdvisorSupport.as_view(), name='support'),
    url(r'^support/forms$', AdvisorForms.as_view(), name='support-forms'),
    url(r'^support/forms/change/firm$', AdvisorChangeDealerGroupView.as_view(), name='support-forms-change-firm'),
    url(r'^support/forms/change/firm/update/(?P<pk>\d+)$', AdvisorChangeDealerGroupUpdateView.as_view()),
    url(r'^support/forms/transfer/single$', AdvisorSingleInvestorTransferView.as_view(), name='support-forms-transfer-single'),
    url(r'^support/forms/transfer/single/update/(?P<pk>\d+)$', AdvisorSingleInvestorTransferUpdateView.as_view()),
    url(r'^support/forms/transfer/bulk$', AdvisorBulkInvestorTransferView.as_view(), name='support-forms-transfer-bulk'),
    url(r'^support/forms/transfer/bulk/update/(?P<pk>\d+)$', AdvisorBulkInvestorTransferUpdateView.as_view()),
    url(r'^support/getting-started$', AdvisorSupportGettingStarted.as_view(), name='support-getting-started'),
    url(r'^summary', AdvisorCompositeSummary.as_view(), name='summary'),
)

# TODO: modularize later
urlpatterns_client = patterns(
    '',
    # OBSELETE. All client routes are handled by React
    # url(r'^app',
    #     ClientApp.as_view(),
    #     name='app-legacy'),
    # url(r'^(?P<slug>[\w-]+)/client/signup/(?P<token>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
    #     ClientSignUp.as_view(),
    #     name='sign_up'),
    # url(r'^(?P<slug>[\w-]+)/client/signup/(?P<token>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<pk>\d+)/(?P<account_token>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
    #     ClientSignUpPrepopulated.as_view()),
    # url(r'^api/account-groups/(?P<pk>\d+)/beneficiaries$',
    #     CancelableTransactionsView.as_view()),
    # url(r'^api/appData',
    #     ClientAppData.as_view(),
    #     name='api:app_data'),
    # url(r'^api/cancelable_transactions',
    #     CancelableTransactionsView.as_view()),
    # url(r'^api/asset-classes',
    #     ClientAssetClasses.as_view(),
    #     name='api:asset_classes'),
    # url(r'^api/user',
    #     ClientUserInfo.as_view(),
    #     name='api:user'),
    # url(r'^api/visitor',
    #     ClientVisitor.as_view(),
    #     name='api:visitor'),
    # url(r'^api/advisors/(?P<pk>\d+)',
    #     ClientAdvisor.as_view(),
    #     name='api:advisors'),
    # url(r'^api/advisors$',
    #     ClientAdvisor.as_view(),
    #     name='api:advisors_2'),
    # url(r'^api/contact-preference$', ContactPreference.as_view()),
    # url(r'^api/accounts$',
    #     csrf_exempt(ClientAccounts.as_view()),
    #     name='api:accounts'),
    # url(r'^api/firms',
    #     ClientFirm.as_view(),
    #     name='api:firms'),
    # url(r'^api/accounts/(?P<pk>\d+)/positions',
    #     ClientAccountPositions.as_view(),
    #     name='api:accounts:positions'),
    # url(r'^api/asset_features',
    #     AssetFeaturesView.as_view(),
    #     name='api:asset_features'),
    # url(r'^api/client/api/accounts/(?P<pk>\d+)/withdrawals$',
    #     csrf_exempt(Withdrawals.as_view())),
    # url(r'^api/portfolio-sets/(?P<pk>\d+)/asset-classes',
    #     PortfolioAssetClasses.as_view(),
    #     name='api:portfolio_sets:asset_classes'),
    # url(r'^api/portfolio-sets/(?P<pk>\d+)/portfolios',
    #     PortfolioPortfolios.as_view(),
    #     name='api:portfolio_sets:portfolios'),
    # url(r'^api/portfolio-sets/(?P<pk>\d+)/risk-free-rates',
    #     PortfolioRiskFreeRates.as_view(),
    #     name='api:portfolio_sets:risk_free_rates'),
    # url(r'^api/client/api/accounts/(?P<pk>\d+)/allocations$',
    #     csrf_exempt(ChangeAllocation.as_view())),
    # url(r'^api/portfolio-sets/goal_(?P<goal_pk>\d+)_(?P<pk>\d+)/asset-classes',
    #     PortfolioAssetClasses.as_view(),
    #     name='api:portfolio_sets:asset_classes'),
    # url(r'^api/portfolio-sets/goal_(?P<goal_pk>\d+)_(?P<pk>\d+)/portfolios',
    #     PortfolioPortfolios.as_view(),
    #     name='api:portfolio_sets:portfolios'),
    # url(r'^api/portfolio-sets/goal_(?P<goal_pk>\d+)_(?P<pk>\d+)/risk-free-rates',
    #     PortfolioRiskFreeRates.as_view(),
    #     name='api:portfolio_sets:risk_free_rates'),
    # url(r'^api/account-groups/(?P<pk>\d+)/pending-invites',
    #     ok_response_json),
    # url(r'^transactions$', csrf_exempt(NewTransactionsView.as_view())),
    # url(r'^transactions\.csv$', csrf_exempt(NewTransactionsView.as_view())),
    # url(r'^api/transaction_memos$',
    #     csrf_exempt(NewTransactionMemoView.as_view())),
    # url(r'^api/accounts/(?P<pk>\d+)$',
    #     csrf_exempt(ChangeGoalView.as_view())),
    # url(r'^api/account-groups/(?P<pk>\d+)/tax-loss-harvesting$',
    #     csrf_exempt(TaxHarvestingView.as_view())),
    # url(r'^automaticDeposit$', csrf_exempt(SetAutoDepositView.as_view())),
    # url(r'^automaticWithdrawal$',
    #     csrf_exempt(SetAutoWithdrawalView.as_view())),
    # url(r'^analysisReturns$', AnalysisReturns.as_view()),
    # url(r'^analysisBalances', AnalysisBalances.as_view()),
    # url(r'^api/zip_codes/(?P<pk>\d+)$', ZipCodes.as_view()),
    # url(r'^api/financial_profile$',
    #     csrf_exempt(FinancialProfileView.as_view())),
    # url(r'^api/financial_plans$',
    #     csrf_exempt(FinancialPlansView.as_view())),
    # url(r'^api/financial_plans/(?P<pk>\d+)$',
    #     csrf_exempt(FinancialPlansView.as_view())),
    # url(r'^api/financial_plans/(?P<pk>\d+)/account_addition$',
    #     csrf_exempt(FinancialPlansAccountAdditionView.as_view())),
    # url(r'^api/financial_plans/account_addition$',
    #     csrf_exempt(FinancialPlansAccountAdditionView.as_view())),
    # url(r'^api/financial_plans/account_removal$',
    #     csrf_exempt(FinancialPlansAccountDeletionView.as_view())),
    # url(r'^api/financial_plans/(?P<pk>\d+)/account_removal$',
    #     csrf_exempt(FinancialPlansAccountDeletionView.as_view())),
    # url(r'^api/external_accounts$',
    #     csrf_exempt(FinancialPlansExternalAccountAdditionView.as_view())),
    # url(r'^api/external_accounts/(?P<pk>\d+)$',
    #     csrf_exempt(FinancialPlansExternalAccountDeletionView.as_view())),
    #
    # url(r'^confirm/account/(?P<pk>\d+)$',
    #     ConfirmClientNewAccount.as_view()),

    # The React code should pick up this route. If it doesn't, there is a configuration problem.
    url(r'^token',
        ClientAppMissing.as_view(),
        name='app'),

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
    url(r'^client/', include(urlpatterns_client, namespace='client')),
    # Advisor views
    url(r'^advisor/', include(urlpatterns_advisor, namespace='advisor')),

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
    url(r'^logout$', Logout.as_view(), name='logout'),
    url(r'^(?P<token>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/legal_signup$',
        AuthorisedRepresentativeSignUp.as_view(),
        name='representative_signup'),
    url(r'^(?P<token>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/advisor_signup',
        AdvisorSignUpView.as_view()),
    url(r'^confirm_email/(?P<type>\d+)/(?P<token>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',
        EmailConfirmationView.as_view()),
    url(r'^confirmation$', Confirmation.as_view(), name='confirmation'),

    url(r'^betasmartz_admin/rebalance/(?P<pk>\d+)$', GoalRebalance.as_view()),
    url('^impersonate/(?P<pk>\d+)$', ImpersonateView.as_view(), name='impersonate'),

    url(r'^password/reset/$',
        'django.contrib.auth.views.password_reset',
        {
            'post_reset_redirect': '/password/reset/done/',
            'template_name': 'registration/password_reset.html'
        },
        name="password_reset"),
    url(r'^password/reset/done/$',
        'django.contrib.auth.views.password_reset_done'),
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
          'show_indexes': True}), )

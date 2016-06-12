from django.conf.urls import patterns, url
from rest_framework_extensions.routers import ExtendedSimpleRouter

from .user import views as user_views
from .settings import views as settings_views
from .client import views as client_views
from .goals import views as goals_views
from .account import views as account_views
from .analysis import views as analysis_views
from .retiresmartz import views as retiresmartz_views


router = ExtendedSimpleRouter(trailing_slash=False)
settings_router = router.register(r'settings',
                                  settings_views.SettingsViewSet,
                                  base_name='settings')
client_router = router.register(r'clients', client_views.ClientViewSet)
client_accounts_router = client_router.register(r'accounts',
                                                account_views.AccountViewSet,
                                                base_name='client-accounts',
                                                parents_query_lookups=['primary_owner'])
retirement_plans_router = client_router.register(r'retirement-plans',
                                                retiresmartz_views.RetiresmartzViewSet,
                                                base_name='client-retirement-plans',
                                                parents_query_lookups=['client'])
goals_router = router.register(r'goals',
                               goals_views.GoalViewSet)
account_router = router.register(r'accounts',
                                 account_views.AccountViewSet)
account_goals_router = account_router.register(r'goals',
                                               goals_views.GoalViewSet,
                                               base_name='accounts-goal',
                                               parents_query_lookups=['account'])
urlpatterns = patterns(
    '',
    url(r'^me/?$', user_views.MeView.as_view(), name='user-me'),
    # reserved # url(r'^me/image/?$', me_views.MeImageView.as_view(), name='me-image'),

    url(r'^login/?$', user_views.LoginView.as_view(), name='user-login'),
    url(r'^returns$', analysis_views.ReturnsView.as_view()),
    # reserved # url(r'^register/?$', user_views.RegisterView.as_view(), name='user-register'),

    # reserved # url(r'^register/reset/?$', user_views.ResetView.as_view(), name='user-reset'),
    # reserved # url(r'^register/send-reset-email/?$', user_views.SendResetEmailView.as_view(), name='user-send-reset-email'),

)

urlpatterns += router.urls

from django.conf.urls import patterns, include, url
from rest_framework import routers

from .user import views as user_views
from .client import views as client_views
from .goals import views as goals_views
from .transactions import views as transactions_views


router = routers.SimpleRouter()
router.register(r'goals', goals_views.GoalViewSet, base_name='goals')


urlpatterns = patterns('',
    #url(r'^$', IndexView.as_view()), # swagger doesn't get it :/

    url(r'^user/?$', user_views.APIUser.as_view(), name='user'), # TODO: obsoleted
    url(r'^user/level/?$', user_views.APIUserLevel.as_view(), name='user-level'), # TODO: obsoleted

    url(r'^me/$', user_views.MeView.as_view(), name='user-me'),
    url(r'^login/$', user_views.LoginView.as_view(), name='user-login'),
    # reserved # url(r'^register/$', user_views.RegisterView.as_view(), name='user-register'),

    # reserved # url(r'^register/reset/$', user_views.ResetView.as_view(), name='user-reset'),
    # reserved # url(r'^register/send-reset-email/$', user_views.SendResetEmailView.as_view(), name='user-send-reset-email'),

    url(r'^client/?$', client_views.APIClient.as_view()), # revise # TODO: should be nested object for /me or /login
    url(r'^client/accounts/?$', client_views.APIClientAccounts.as_view()), # revise # TODO: should be /me/accounts

    # obsoleted # url(r'^goal-types/?$', goals_views.APIGoalTypes.as_view()), # revise
    # obsoleted # url(r'^goals/?$', goals_views.APIGoal.as_view()), # revise

    url(r'^transactions/deposit/?$', transactions_views.APITransactionsDeposit.as_view()),
)

urlpatterns += router.urls
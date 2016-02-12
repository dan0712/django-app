from django.conf.urls import patterns, include, url
from api.v1.transactions.views import *

urlpatterns = patterns('',

                       (r'^api/v1/transactions/deposit/?$', APITransactionsDeposit.as_view()),
)

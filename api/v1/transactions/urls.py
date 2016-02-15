from django.conf.urls import patterns, include, url
from api.v1.transactions.views import *

urlpatterns = patterns('',
    (r'^transactions/deposit/?$', APITransactionsDeposit.as_view()),
)

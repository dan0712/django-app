from django.conf.urls import patterns, include, url
from api.v1.goals.views import *

urlpatterns = patterns('',
    (r'^goal/types/?$', APIGoalTypes.as_view()),
    (r'^goals/?$', APIGoal.as_view()),
)

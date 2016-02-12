from django.conf.urls import patterns, include, url
from api.v1.goals.views import *

urlpatterns = patterns('',

                       (r'^api/v1/goal/types/?$', APIGoalTypes.as_view()),
                       (r'^api/v1/goals/?$', APIGoals.as_view()),
)

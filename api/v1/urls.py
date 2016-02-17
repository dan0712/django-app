from django.conf.urls import include, url

urlpatterns = [
    url(r'', include('api.v1.user.urls')),
    url(r'', include('api.v1.client.urls')), # TODO: mount on clients/
    url(r'', include('api.v1.goals.urls')), # TODO: mount on goals/
    url(r'', include('api.v1.transactions.urls')), # TODO: mount on transactions/
]

from django.conf.urls import include, url

urlpatterns = [
    url(r'', include('api.v1.user.urls')),
    url(r'', include('api.v1.client.urls')),
    url(r'', include('api.v1.goals.urls')),
]

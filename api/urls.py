from django.urls import include, path
from .views import api_view

urlpatterns = [
    path('', api_view, name='api_view' ),
     path('apps/', include('apps.urls')),
]

from django import views
from django.contrib import admin
from django.urls import path , include
from apps.views import login_view


urlpatterns = [
    path('',login_view, name='login'),
    path('admin/', admin.site.urls),
    path('apps/',include('django.contrib.auth.urls')),
    path('apps/', include('apps.urls')),

]

#endpoint ='http://127.0.0.1:8000/api'python manage.py runserver

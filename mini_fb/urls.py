from django.urls import path
from django.conf import settings
from . import views


urlpatterns = [
    path(r'', views.main, name="mini_fb"),
    
]

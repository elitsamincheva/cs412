from django.urls import path
from django.conf import settings
from . import views


urlpatterns = [
    path(r'', views.main, name="restaurant"),
    path(r'order', views.order, name="order"),
    path(r'confirmation', views.confirmation, name="confirmation"),
]


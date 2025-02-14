# restaurant/urls.py
# ------------------------------------------------------------------------------
# This file defines the URL patterns for the restaurant's ordering system.
# 
# The URL patterns include:
# 1. An empty path ('') mapped to the `main` view, which displays the main page of 
#    the restaurant that includes basic onfo about the restaurant.
# 2. The path 'order' mapped to the `order` view, which displays the order form 
#    with menu items and a randomly selected daily special.
# 3. The path 'confirmation' mapped to the `confirmation` view, which shows 
#    the order summary, including customer info and a randomly generated ready time.
#
# The URL paths use the Django `path` function to map each URL to its corresponding view.
# ------------------------------------------------------------------------------

from django.urls import path
from django.conf import settings
from . import views


urlpatterns = [
    path(r'', views.main, name="restaurant"),
    path(r'order', views.order, name="order"),
    path(r'confirmation', views.confirmation, name="confirmation"),
]


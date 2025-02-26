# URL configuration for Mini FB
# - Maps root URL to ShowAllProfilesView for displaying all profiles
# - Maps profile URL with primary key (pk) to ProfileView for individual profile pages

from django.urls import path
from django.conf import settings
from . import views
from .views import ShowAllProfilesView, ProfileView, CreateProfileView, CreateStatusMessageView

urlpatterns = [
    path(r'', ShowAllProfilesView.as_view(), name="show_all_profiles"),
    path(r'profile/<int:pk>', ProfileView.as_view(), name="profile"), 
    path(r'create_profile', CreateProfileView.as_view(), name="create_profile_form"), 
    path(r'profile/<int:pk>/create_status', CreateStatusMessageView.as_view(), name="create_status"), 
]

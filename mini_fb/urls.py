# URL Configuration for Mini FB
# - Defines URL patterns for navigating between different views
# - Maps URLs to corresponding class-based views in views.py

from django.urls import path
from django.conf import settings
from . import views
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Root URL: Displays a list of all profiles
    path(r'', ShowAllProfilesView.as_view(), name="show_all_profiles"),
    # Profile Page: Displays an individual user's profile, identified by primary key (pk)
    path(r'profile/<int:pk>', ProfileView.as_view(), name="profile"), 
    # Create Profile: Displays form for creating a new user profile
    path(r'create_profile', CreateProfileView.as_view(), name="create_profile_form"), 
    # Create Status: Displays form for posting a new status message for a specific profile
    path(r'profile/<int:pk>/create_status', CreateStatusMessageView.as_view(), name="create_status"), 
    # Update Profile: Displays form for updating an existing profile
    path(r'profile/<int:pk>/update', UpdateProfileView.as_view(), name="update_profile"),
    # Update Status Message: displays form to update the text of the StatusMessage
    path('status/<int:pk>/update', UpdateStatusMessageView.as_view(), name="update_status"),
    # Delete Status Message
    path('status/<int:pk>/delete', DeleteStatusMessageView.as_view(), name="delete_status"),
    # Create a Friend relationship between 2 profiles
    path('profile/<int:pk>/add_friend/<int:other_pk>/', AddFriendView.as_view(), name='add_friend'),
    # View the list of friend suggestions for a profile
    path('profile/<int:pk>/friend_suggestions/', ShowFriendSuggestionsView.as_view(), name='friend_suggestions'),
    # View the news feed of a profile and its friends
    path('profile/<int:pk>/news_feed/', ShowNewsFeedView.as_view(), name='news_feed'),
    # auth related urls
    path('login/', auth_views.LoginView.as_view(template_name='mini_fb/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='show_all_profiles'), name='logout'),
]


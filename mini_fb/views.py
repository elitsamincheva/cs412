# views.py for Mini FB
# - ShowAllProfilesView: Displays a list of all profiles
# - ProfileView: Displays a single profile based on the profile's primary key (pk)

from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Profile

# Create your views here.
class ShowAllProfilesView(ListView):
    '''define a view class to show all the fb profiles'''
    model = Profile
    template_name = "mini_fb/show_all_profiles.html"
    context_object_name = "profiles"

class ProfileView(DetailView):
    '''display a single profile'''
    model = Profile
    template_name = "mini_fb/profile.html"
    context_object_name = "profile"
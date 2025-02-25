# views.py for Mini FB
# - ShowAllProfilesView: Displays a list of all profiles
# - ProfileView: Displays a single profile based on the profile's primary key (pk)
# - CreateProfileView: create a new profile in the FB

from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from .models import Profile
from .forms import CreateProfileForm

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

class CreateProfileView(CreateView):
    '''Create a new profile'''
    model = Profile
    form_class = CreateProfileForm
    template_name = "mini_fb/create_profile_form.html"

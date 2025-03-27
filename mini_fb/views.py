# views.py for Mini FB
# - ShowAllProfilesView: Displays a list of all profiles
# - ProfileView: Displays a single profile based on the profile's primary key (pk)
# - CreateProfileView: Create a new profile in the FB
# - CreateStatusMessageView: Create a new status message for a Profile, can add photos to go along with the status message
# - UpdateProfileView: View to update an existing profile
# - UpdateStatusMessageView: View to update the text of an existing status message
# - DeleteStatusMessageView: View to delete an existing status message
# - AddFriendView: Handles the logic for adding a friend to a profile
# - ShowFriendSuggestionsView: Displays friend suggestions for a profile
# - ShowNewsFeedView: Displays a news feed for a profile (including status messages of the profile and its friends)

from typing import Any
from django.http.request import HttpRequest as HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from .models import Profile, StatusMessage, Image, StatusImage
from .forms import CreateProfileForm, CreateStatusMessageForm, UpdateProfileForm
from django.contrib.auth.mixins import LoginRequiredMixin

class ShowAllProfilesView(ListView):
    '''define a view class to show all the fb profiles'''
    model = Profile
    template_name = "mini_fb/show_all_profiles.html"
    context_object_name = "profiles"

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            print(f'ShowAllProfilesView.dispatch(): request.user={request.user}')
        else:
            print(f'ShowAllProfilesView.dispatch(): not logged in.')

        return super().dispatch(request, *args, **kwargs)

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

class CreateStatusMessageView(LoginRequiredMixin, CreateView):
    '''create a new status message and save it to the database'''

    form_class = CreateStatusMessageForm
    template_name = "mini_fb/create_status_form.html"

    def get_login_url(self) -> str:
        return reverse('login')

    def get_context_data(self):
        '''Return the dictionary of context variables for use in the template'''
        context = super().get_context_data()
        # retrieve the PK from the URL pattern
        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        # add this profile into the context dictionary:
        context['profile'] = profile
        return context

    def form_valid(self, form):
        """Handle the form submission, save the new status message, and associate uploaded images."""
        # print(f"CreateStatusMessageView.form_valid: form.cleaned_data={form.cleaned_data}")
        
        # retrieve the profile based on the PK from the URL
        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        
        # attach this profile to the status message and save it
        form.instance.profile = profile  
        sm = form.save()  # save status message and get the reference

        # Read uploaded files
        files = self.request.FILES.getlist('files')  
        # print(f"Uploaded files: {files}")  

        # process each uploaded file
        for file in files:
            # create and save an image object
            img = Image(profile=profile, image_file=file)
            img.save()
            # create and save a StatusImage object linking the image and status message
            status_img = StatusImage(status_message=sm, image=img)
            status_img.save()
            # print(f"Saved image {img.id} and linked it to status message {sm.id}")
        return super().form_valid(form)

        
    def get_success_url(self):
        '''provide a URL to redirect to after creating a new StatusMessage'''
        # retrieve the PK from the URL pattern
        pk = self.kwargs['pk']
        # call reverse to generate the URL for this Profile
        return reverse('profile', kwargs={'pk': pk})
    

class UpdateProfileView(LoginRequiredMixin, UpdateView):
    """view for updating an existing profile"""
    model = Profile
    form_class = UpdateProfileForm
    template_name = "mini_fb/update_profile_form.html"

    def get_login_url(self) -> str:
        return reverse('login')

    def get_success_url(self):
        """redirect to the updated profile's detail page after a successful update"""
        return reverse('profile', kwargs={'pk': self.object.pk})
    
class UpdateStatusMessageView(LoginRequiredMixin, UpdateView):
    '''view for updating the text of the status message'''
    model = StatusMessage
    fields = ['message']
    template_name = "mini_fb/update_status_form.html"
    context_object_name = "status"

    def get_login_url(self) -> str:
        return reverse('login')

    def get_success_url(self):
        '''Redirects to the user's profile page after a successful update'''
        return reverse('profile', kwargs={'pk': self.object.profile.pk})

class DeleteStatusMessageView(LoginRequiredMixin, DeleteView):
    '''view for deleting a status message'''
    model = StatusMessage
    template_name = "mini_fb/delete_status_form.html"
    context_object_name = "status"

    def get_login_url(self) -> str:
        return reverse('login')

    def get_success_url(self):
        '''Redirects to the user's profile page after successful deletion'''
        return reverse('profile', kwargs={'pk': self.object.profile.pk})
    
class AddFriendView(LoginRequiredMixin, View):
    """this view handles the logic for adding a friend to a profile"""

    def get_login_url(self) -> str:
        return reverse('login')

    def dispatch(self, request, *args, **kwargs):
        """Retrieve profiles and add a friend then redirect to the profile page"""
        # get the two profile objects based on the URL parameters
        profile = get_object_or_404(Profile, pk=kwargs['pk'])
        other_profile = get_object_or_404(Profile, pk=kwargs['other_pk'])

        # call the add friend method from the Profile model
        profile.add_friend(other_profile)

        # redirect to the profile page after adding the friend
        return redirect('profile', pk=profile.pk)
    

class ShowFriendSuggestionsView(LoginRequiredMixin, DetailView):
    """
    Displays the friend suggestions for a given profile
    
    This view fetches and displays a list of suggested friends for the profile 
    based on the profile's current friends and their connections. The suggestions
    are generated by a method in the Profile model called get_friend_suggestions
    """
    model = Profile
    template_name = 'mini_fb/friend_suggestions.html'
    context_object_name = 'profile'

    def get_login_url(self) -> str:
        return reverse('login')

    def get_context_data(self, **kwargs):
        """
        Adds the friend suggestions to the context dictionary

        Retrieves the profile object and uses it to fetch the friend suggestions,
        which are then added to the context for rendering in the template
        """
        # Get the profile instance
        context = super().get_context_data(**kwargs)
        
        # Get the friend suggestions for the current profile
        profile = self.get_object()
        context['friend_suggestions'] = profile.get_friend_suggestions()
        
        return context
    
class ShowNewsFeedView(LoginRequiredMixin, DetailView):
    """
    Displays the news feed for a given profile
    
    The news feed consists of the status messages from the profile and its friends
    The status messages are fetched using the get_news_feed method in the Profile model
    """
    model = Profile
    template_name = 'mini_fb/news_feed.html'
    context_object_name = 'profile'

    def get_login_url(self) -> str:
        return reverse('login')

    def get_context_data(self, **kwargs):
        """
        Adds the news feed (status messages of the profile and its friends) to the context

        Retrieves the profile object and uses it to fetch the news feed, which is then 
        added to the context for rendering in the template
        """
        context = super().get_context_data(**kwargs)
        profile = self.get_object()  # get the profile object

        # get the news feed for the profile
        context['news_feed'] = profile.get_news_feed()
        return context
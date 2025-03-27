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

class BaseView(View):
    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            
            # Add the logged-in user's profile to the context, if authenticated
            if self.request.user.is_authenticated:
                logged_in_profile = Profile.objects.filter(user=self.request.user).first()  # Assuming Profile is related to the User model
                context['logged_in_profile'] = logged_in_profile

            return context

class ShowAllProfilesView(BaseView, ListView):
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
    
    
   

class ProfileView(BaseView, DetailView):
    '''display a single profile'''
    model = Profile
    template_name = "mini_fb/profile.html"
    context_object_name = "profile"


    

class CreateProfileView(BaseView, CreateView):
    '''Create a new profile'''
    model = Profile
    form_class = CreateProfileForm
    template_name = "mini_fb/create_profile_form.html"

class CreateStatusMessageView(BaseView, LoginRequiredMixin, CreateView):
    '''create a new status message and save it to the database'''

    form_class = CreateStatusMessageForm
    template_name = "mini_fb/create_status_form.html"

    def get_login_url(self) -> str:
        return reverse('login')
    
    def get_context_data(self, **kwargs):
        '''Return the dictionary of context variables for use in the template'''
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(Profile, user=self.request.user)  # get profile from logged in user
        context['profile'] = profile
        return context

    def form_valid(self, form):
        """Handle form submission and associate with the logged-in user's profile."""
        profile = get_object_or_404(Profile, user=self.request.user)  # get profile
        form.instance.profile = profile  
        sm = form.save()  # save status message

        # handle uploaded files
        files = self.request.FILES.getlist('files')  
        for file in files:
            img = Image(profile=profile, image_file=file)
            img.save()
            status_img = StatusImage(status_message=sm, image=img)
            status_img.save()
        return super().form_valid(form)

    def get_success_url(self):
        '''Redirect to the profile page after creating a new status'''
        return reverse('profile', kwargs={'pk': self.object.profile.pk})

 
class UpdateProfileView(BaseView, LoginRequiredMixin, UpdateView):
    """view for updating an existing profile"""
    model = Profile
    form_class = UpdateProfileForm
    template_name = "mini_fb/update_profile_form.html"

    def get_login_url(self) -> str:
        return reverse('login')
    
    def get_object(self):
        """retrieve the profile of the currently logged in user"""
        return get_object_or_404(Profile, user=self.request.user)

    def get_success_url(self):
        """redirect to the updated profile's detail page after a successful update"""
        return reverse('profile', kwargs={'pk': self.object.pk})



    
class UpdateStatusMessageView(BaseView, LoginRequiredMixin, UpdateView):
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

class DeleteStatusMessageView(BaseView, LoginRequiredMixin, DeleteView):
    '''view for deleting a status message'''
    model = StatusMessage
    template_name = "mini_fb/delete_status_form.html"
    context_object_name = "status"

    def get_login_url(self) -> str:
        return reverse('login')

    def get_success_url(self):
        '''Redirects to the user's profile page after successful deletion'''
        return reverse('profile', kwargs={'pk': self.object.profile.pk})
    
class AddFriendView(BaseView, LoginRequiredMixin, View):
    """this view handles the logic for adding a friend to a profile"""

    def get_login_url(self) -> str:
        return reverse('login')

    def dispatch(self, request, *args, **kwargs):
        """Retrieve profiles and add a friend then redirect to the profile page"""
        # get the two profile objects based on the URL parameters
        profile = get_object_or_404(Profile, user=request.user) # get logged in user's profile
        other_profile = get_object_or_404(Profile, pk=kwargs['other_pk'])

        # call the add friend method from the Profile model
        profile.add_friend(other_profile)

        # redirect to the profile page after adding the friend
        return redirect('profile', pk=profile.pk)
    

class ShowFriendSuggestionsView(BaseView, LoginRequiredMixin, DetailView):
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
    
    def get_object(self):
        """Retrieve the profile of the currently logged-in user"""
        return get_object_or_404(Profile, user=self.request.user)
    
class ShowNewsFeedView(BaseView, LoginRequiredMixin, DetailView):
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


    def get_object(self):
        """Retrieve the profile of the currently logged-in user"""
        return get_object_or_404(Profile, user=self.request.user)

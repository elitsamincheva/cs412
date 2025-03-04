# views.py for Mini FB
# - ShowAllProfilesView: Displays a list of all profiles
# - ProfileView: Displays a single profile based on the profile's primary key (pk)
# - CreateProfileView: create a new profile in the FB
# - CreateStatusMessageView: create a new status message for a Profile, can add photos to go along with the status message

from django.urls import reverse
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from .models import Profile, StatusMessage, Image, StatusImage
from .forms import CreateProfileForm, CreateStatusMessageForm

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

class CreateStatusMessageView(CreateView):
    '''create a new status message and save it to the database'''

    form_class = CreateStatusMessageForm
    template_name = "mini_fb/create_status_form.html"

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
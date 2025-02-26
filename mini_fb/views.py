# views.py for Mini FB
# - ShowAllProfilesView: Displays a list of all profiles
# - ProfileView: Displays a single profile based on the profile's primary key (pk)
# - CreateProfileView: create a new profile in the FB

from django.urls import reverse
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from .models import Profile, StatusMessage
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
    '''A view to create a new status message and save it to the database.'''

    form_class = CreateStatusMessageForm
    template_name = "mini_fb/create_status_form.html"

    def get_context_data(self):
        '''Return the dictionary of context variables for use in the template.'''

        # calling the superclass method
        context = super().get_context_data()

        # retrieve the PK from the URL pattern
        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)

        # add this profile into the context dictionary:
        context['profile'] = profile
        return context

    def form_valid(self, form):
        '''This method handles the form submission and saves the 
        new object to the Django database.
        We need to add the foreign key (of the Profile) to the StatusMessage
        object before saving it to the database.
        '''

        # instrument our code to display form fields: 
        print(f"CreateStatusMessageView.form_valid: form.cleaned_data={form.cleaned_data}")
        
        # retrieve the PK from the URL pattern
        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        
        # attach this profile to the status message
        form.instance.profile = profile  # set the FK

        # delegate the work to the superclass method form_valid:
        return super().form_valid(form)
        
    def get_success_url(self):
        '''Provide a URL to redirect to after creating a new StatusMessage.'''

        # retrieve the PK from the URL pattern
        pk = self.kwargs['pk']
        
        # call reverse to generate the URL for this Profile
        return reverse('profile', kwargs={'pk': pk})
# Forms for Mini FB
# - Defines form classes for creating user profiles and status messages
# - Uses Django's ModelForm to generate forms based on the Profile and StatusMessage models

from django import forms
from django import forms
from .models import Profile, StatusMessage

class CreateProfileForm(forms.ModelForm):
    """Form for creating a new user profile, including basic personal details"""

    class Meta:
        model = Profile # specifies the model to base the form on
        fields = ['first_name', 'last_name', 'city', 'email', 'image_file']  # Fields included in the form

class CreateStatusMessageForm(forms.ModelForm):
    """Form for creating a new status message associated with a profile"""

    class Meta:
        model = StatusMessage   
        fields = ['message']    # Only includes the message field, as timestamp is auto-generated

class UpdateProfileForm(forms.ModelForm):
    '''Form for updating an existing user profile, excluding first and last name'''
    
    class Meta:
        model = Profile
        fields = ['city', 'email', 'image_file']
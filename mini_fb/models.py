# Model defns for Mini FB
# - Defines the Profile model, which includes fields like first name, last name, city, and profile image URL
# - Used to store and manage user profile data

from django.db import models
from django.urls import reverse

class Profile(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    profile_image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_status_messages(self):
        """Returns all status messages for this profile ordered by timestamp (newest first)"""
        return self.status_messages.all().order_by('-timestamp') 
    
    def get_absolute_url(self):
        '''return the URl to display the profile that was just created'''
        return reverse('profile', kwargs={'pk':self.pk})



class StatusMessage(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True) 
    message = models.TextField() 
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="status_messages")  # link the status message to the associated profile

    def __str__(self):
        return f"Status by {self.profile.first_name} {self.profile.last_name} at {self.timestamp}: {self.message[:50]}..."

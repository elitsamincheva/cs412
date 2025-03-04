# Models for Mini FB
# - Defines the Profile model for user profiles
# - Defines the StatusMessage model for status updates associated with profiles

from django.db import models
from django.urls import reverse

class Profile(models.Model):
    """Model representing a user profile with basic personal information"""
    first_name = models.CharField(max_length=50)    # user's first name
    last_name = models.CharField(max_length=50)     # user's last name
    city = models.CharField(max_length=100)         # city of residence
    email = models.EmailField(unique=True)          # unique email for each profile
    # profile_image_url = models.URLField(blank=True, null=True)  # profile image URL
    image_file = models.ImageField(blank=True)

    def __str__(self):
        """Returns a string representation of the profile (full name)"""
        return f"{self.first_name} {self.last_name}"

    def get_status_messages(self):
        """Returns all status messages for this profile ordered by timestamp (newest first)"""
        return self.status_messages.all().order_by('-timestamp') 
    
    def get_absolute_url(self):
        '''return the URl to display the profile that was just created'''
        return reverse('profile', kwargs={'pk':self.pk})



class StatusMessage(models.Model):
    """Model representing a status message posted by a user profile"""
    timestamp = models.DateTimeField(auto_now_add=True) # timestamp of message creation
    message = models.TextField()    # the actual status emssage content
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="status_messages")  # link the status message to the associated profile

    def get_images(self):
        '''returns all of the images associated with the status message'''
        return Image.objects.filter(status_images__status_message=self)


    def __str__(self):
        """Returns a string representation of the status message (truncated for display)"""
        return f"Status by {self.profile.first_name} {self.profile.last_name} at {self.timestamp}: {self.message[:50]}..."


class Image(models.Model):
    '''model representing an uploaded image stored in the media directory'''
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="images")   # link the image to the profile
    image_file = models.ImageField(upload_to='images/')
    timestamp = models.DateTimeField(auto_now_add=True)
    caption = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Image uploaded by {self.profile.first_name} {self.profile.last_name} on {self.timestamp}" 
    
class StatusImage(models.Model):
    '''model respresenting relationship between status message and image'''
    status_message = models.ForeignKey(StatusMessage, on_delete=models.CASCADE, related_name="status_images")
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name="status_images")

    def __str__(self):
        return f"Image {self.image.id} linked to Status {self.status_message.id}"

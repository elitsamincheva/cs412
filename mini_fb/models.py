# Models for Mini FB
# - Defines the Profile model for user profiles
# - Defines the StatusMessage model for status updates associated with profiles

from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db.models import Q

class Profile(models.Model):
    """Model representing a user profile with basic personal information"""
    first_name = models.CharField(max_length=50)    # user's first name
    last_name = models.CharField(max_length=50)     # user's last name
    city = models.CharField(max_length=100)         # city of residence
    email = models.EmailField(unique=True)          # unique email for each profile
    image_file = models.ImageField(blank=True)      # profile pic image upload

    def __str__(self):
        """Returns a string representation of the profile (full name)"""
        return f"{self.first_name} {self.last_name}"

    def get_status_messages(self):
        """Returns all status messages for this profile ordered by timestamp (newest first)"""
        return self.status_messages.all().order_by('-timestamp') 
    
    def get_absolute_url(self):
        '''return the URl to display the profile that was just created'''
        return reverse('profile', kwargs={'pk':self.pk})
    
    def get_friends(self):
        """returns a list of friends associated with this profile"""
        # query the Friend model for records where this profile is either profile1 or profile2
        friends = Friend.objects.filter(
            models.Q(profile1=self) | models.Q(profile2=self)
        )

        # create a list of friends profiles by checking both profile1 and profile2
        friends_profiles = []
        for friend in friends:
            if friend.profile1 != self:
                friends_profiles.append(friend.profile1)
            if friend.profile2 != self:
                friends_profiles.append(friend.profile2)

        return friends_profiles
    
    def add_friend(self, other):
        # check if self and other are the same profile to avoid self friending
        if self == other:
            raise ValidationError("You can't friend yourself")
        
        # check if a friend relation already exists b/t self and the other profile
        if not Friend.objects.filter(
            (Q(profile1=self) & Q(profile2=other)) | (Q(profile1=other) & Q(profile2=self))
        ).exists():
            Friend.objects.create(profile1=self, profile2=other)
        else:
            print("they are already friends")


    def get_friend_suggestions(self):
        # Get a list of all profiles excluding the current one
        all_profiles = Profile.objects.exclude(id=self.id)
        
        # Get the list of profiles already friends with the current profile
        friends = self.get_friends()

        # Get friends of friends by iterating over the current profile's friends
        friends_of_friends = []
        for friend in friends:
            friends_of_friends.extend(friend.get_friends())

        # Filter out the current profile and existing friends from the friends of friends list
        friend_suggestions = [profile for profile in friends_of_friends if profile != self and profile not in friends]

        # Return the non-friends as friend suggestions
        return Profile.objects.filter(id__in=[profile.id for profile in friend_suggestions])



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


class Friend(models.Model):
    '''model representing the relationship between 2 profiles'''
    profile1 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="profile1")
    profile2 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="profile2")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile1.first_name} {self.profile1.last_name} is friends with {self.profile2.first_name} {self.profile2.last_name}"
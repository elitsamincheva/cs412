# Model defns for Mini FB
# - Defines the Profile model, which includes fields like first name, last name, city, and profile image URL
# - Used to store and manage user profile data

from django.db import models

class Profile(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    profile_image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

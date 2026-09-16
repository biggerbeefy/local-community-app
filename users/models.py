import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Fixes the sequential ID scraping vulnerability by using random UUID strings
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Custom fields for our Eventbrite/Nextdoor mashup
    bio = models.TextField(max_length=500, blank=True)
    location_zip = models.CharField(max_length=10, blank=True)
    is_verified_resident = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)

    def __str__(self):
        return self.username

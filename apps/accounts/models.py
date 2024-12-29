from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    member_id = models.IntegerField(null=False, blank=False)  
    profile_picture = models.ImageField(upload_to="profile_picture/%Y/%m/%d/", blank=True)
    access_token = models.TextField(
        blank=False,  
        null=False,  
        editable=False,
    )
    refresh_token = models.TextField(
        blank=False,  
        null=False,  
        editable=False,
    )

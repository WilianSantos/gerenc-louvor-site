from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxLengthValidator

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


class TokenRecord(models.Model):
    temporary_token = models.TextField(editable=False)
    email = models.EmailField()
    is_used = models.BooleanField(default=False, editable=False)

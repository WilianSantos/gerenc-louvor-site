from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    member_id = models.IntegerField(null=False, blank=False)  



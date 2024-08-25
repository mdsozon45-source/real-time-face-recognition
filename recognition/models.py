from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class UserProfile(AbstractUser):
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    encoding = models.JSONField(null=True, blank=True)  

    def __str__(self):
        return self.username

class RecognizedFace(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='recognized_faces/')
    video = models.FileField(upload_to='recognized_videos/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} recognized at {self.timestamp}" if self.user else "Unknown face"
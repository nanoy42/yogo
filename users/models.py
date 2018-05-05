from django.db import models
from django.contrib.auth.models import User

class TelegramPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)
    verifyToken = models.TextField(max_length=255, blank=True)
    notifyProject = models.BooleanField(default=False)
    notifyTask = models.BooleanField(default=False)
    notifyProfile = models.BooleanField(default=False)
    chatId = models.IntegerField(default=0, null=True, blank=True)

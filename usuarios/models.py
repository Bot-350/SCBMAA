from django.db import models
from django.contrib.auth.models import User

from django.utils import timezone # Import timezone

class SearchLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    term = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now) # Changed auto_now_add=True to default=timezone.now

    def __str__(self):
        return f"{self.user.username} searched for '{self.term}' at {self.timestamp}"

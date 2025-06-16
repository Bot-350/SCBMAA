from django.db import models
from django.contrib.auth.models import User

class SearchLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    term = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} searched for '{self.term}' at {self.timestamp}"

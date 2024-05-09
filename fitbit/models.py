from django.db import models

class FitbitUser(models.Model):
    user_id = models.CharField(max_length=100, unique=True)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    token_expiry = models.DateTimeField()

    def __str__(self):
        return self.user_id

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Identity(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    key = models.CharField(max_length=60, unique=True)
    is_virtual = models.BooleanField(default=True)
    email_is_valid = models.BooleanField(default=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['-creation_date']),
            models.Index(fields=['key'])
        ]

    def __str__(self):
        return self.key
from django.db import models
from django.contrib.auth.models import User
from off.elements.models import Element


class UserElement(Element):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

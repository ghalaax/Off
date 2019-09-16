from django.db import models
from off.elements.models import Element, ElementMetadata, ElementHistory, Permissions
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from off.elements.services import element_metadata
from off.elements.tools import hooks

# Create your models here.

class Forum(Element):
    federates = models.ManyToManyField(User, symmetrical=False,
                                    through='ForumPart',
                                    through_fields=('community', 'federate'))


class ForumPart(models.Model):
    community = models.ForeignKey(Forum, on_delete=models.CASCADE)
    federate = models.ForeignKey(User, on_delete=models.CASCADE)
    part_on = models.DateTimeField(auto_now_add=True)
    alive = models.BooleanField(default=True)

@receiver(post_save, sender=Forum)
def onForumCreateMetadata(instance, created, **kwargs):
    element_metadata.Services.createElementMetadata(instance.element_ptr, created, Permissions.r | Permissions.w)
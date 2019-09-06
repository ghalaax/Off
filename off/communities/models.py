from django.db import models
from off.elements.models import Element, ElementMetadata
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Community(Element):
    federates = models.ManyToManyField(User, symmetrical=False,
                                    through='CommunityPart',
                                    through_fields=('community', 'federate'))


class CommunityPart(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    federate = models.ForeignKey(User, on_delete=models.CASCADE)
    part_on = models.DateTimeField(auto_now_add=True)
    alive = models.BooleanField(default=True)

@receiver(post_save, sender=Community)
def create_community_metadata(sender, instance, created, **kwargs):
    if created:
        ElementMetadata.objects.create(element=instance.element_ptr, permissions=0)

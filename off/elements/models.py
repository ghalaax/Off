from django.db import models
from django.contrib.auth.models import User
from django.db import signals
from martor.models import MartorField
import uuid


class Element(models.Model):
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    content = MartorField(max_length=4096)
    links = models.ManyToManyField('self',
                                   symmetrical=False,
                                   through='ElementLink',
                                   through_fields=('subject', 'object'))
    created_on = models.DateTimeField(auto_now_add=True)
    alive = models.BooleanField(default=True)


class ElementLink(Element):
    class Meta:
        unique_together = ['subject', 'object']
    subject = models.ForeignKey(
        Element, on_delete=models.CASCADE, related_name='link_startpoints')
    object = models.ForeignKey(
        Element, on_delete=models.CASCADE, related_name='link_endpoints')


class UserElement(Element):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

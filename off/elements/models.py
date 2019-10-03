from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import pre_save
from martor.models import MartorField
import hashlib
import uuid


class Element(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['uid'])
        ]
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    data = models.BinaryField(null=True)
    data_checksum = models.BinaryField(max_length=64, editable=False, null=True)
    links = models.ManyToManyField('self',
                                   symmetrical=False,
                                   through='ElementLink',
                                   through_fields=('subject', 'object'))
    created_on = models.DateTimeField(auto_now_add=True)
    alive = models.BooleanField(default=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        update_fields = list(update_fields)
        if self.data:
            new_checksum = hashlib.sha256(self.data).hexdigest().encode('utf-8')
            if new_checksum != self.data_checksum:
                self.data_checksum = new_checksum
                update_fields.append('data_checksum')
        else:
            self.data_checksum = None
            update_fields.append('data_checksum')

        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)


class ElementLink(Element):
    class Meta:
        unique_together = ['subject', 'object']
    subject = models.ForeignKey(
        Element, on_delete=models.CASCADE, related_name='link_startpoints')
    object = models.ForeignKey(
        Element, on_delete=models.CASCADE, related_name='link_endpoints')

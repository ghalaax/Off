from off.elements.services import element_metadata
from django.db.models.signals import post_save
from django.dispatch import receiver

def createMetadata(instance, created, permissions=0, **kwargs):
    if created:
        element_metadata.Services.createElementMetadata(instance.element_ptr, permissions)

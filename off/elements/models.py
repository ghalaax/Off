from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from enum import IntFlag, IntEnum
import uuid

class Element(models.Model):
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    title = models.CharField(blank=True, null=True, max_length=255)
    description = models.TextField(blank=True, null=True, max_length=1024)
    tags = models.CharField(blank=True, null=True, max_length=255)
    links = models.ManyToManyField( 'self', 
                                    symmetrical=False,
                                    through='ElementLink',
                                    through_fields=('node', 'sibling'))
    
    def __str__(self):
        return str(self.uid)

class Permissions(IntFlag):
    x = 1
    w = 2
    r = 4

class PermissionsShift(IntEnum):
    u = 6
    g = 3
    a = 0

class ElementMetadata(models.Model):
    element = models.ForeignKey(Element, on_delete=models.CASCADE, related_name='metadata')
    created_on = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_elements')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_elements')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True, null=True)
    # unix style binary permissions (u+rwx g+rwx a+rwx)
    permissions = models.PositiveSmallIntegerField()

    def __str__(self):
        return str(self.element)

    def get_user_permissions(self, user):
        permission_shift = PermissionsShift.a
        if self.group is None or user.groups.filter(id=self.group.id).exists():
            permission_shift = PermissionsShift.g
        if self.owner is None or user == self.owner:
            permission_shift = PermissionsShift.u
        return self.permissions >> permission_shift
    
    def can(self, user_permissions, permission):
        return True if user_permissions & permission else False
    def can_read(self, user_permissions):
        return self.can(user_permissions, Permissions.r)
    def can_write(self, user_permissions):
        return self.can(user_permissions, Permissions.w)
    def can_execute(self, user_permissions):
        return self.can(user_permissions, Permissions.x)
    def can_cross(self, user_permissions):
        return self.can(user_permissions, Permissions.x)

    def set_scope_permissions(self, permissions, shift, commit=True):
        remove_permissions = ~((Permissions.x | Permissions.r | Permissions.w) << shift)
        new_permissions = permissions << shift
        self.set_permissions((self.permissions & remove_permissions) | new_permissions, commit=commit)
    def set_permissions(self, permissions, commit=True):
        self.permissions = permissions
        if commit:
            self.save(update_fields=['permissions'])

@receiver(post_save, sender=Element)
def create_element_metadata(sender, instance, created, **kwargs):
    if created:
        ElementMetadata.objects.create(element=instance, permissions=0)
        ElementHistory.objects.create(element=instance, change='# creation #')

class ElementHistory(models.Model):
    element = models.ForeignKey(Element, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    change = models.CharField(max_length=1024)

    def __str__(self):
        return str(self.date) + ':' + str(self.element)
    
class ElementLinkType(models.Model):
    name = models.CharField(max_length=32)
    algorithm = models.CharField(max_length=32)

    def __str__(self):
        return self.name

class ElementLink(models.Model):
    node = models.ForeignKey(Element, on_delete=models.CASCADE, related_name='link_startpoints')
    sibling = models.ForeignKey(Element, on_delete=models.CASCADE, related_name='link_endpoints')
    type = models.ForeignKey(ElementLinkType, on_delete=models.SET_NULL, null=True)
    linked_on = models.DateTimeField(auto_now_add=True)
    alive = models.BooleanField(default=True)


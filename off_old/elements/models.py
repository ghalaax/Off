from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from martor.models import MartorField
from enum import IntFlag, IntEnum
import uuid


class Element(models.Model):
    __element_related_name__ = None
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    title = models.CharField(blank=True, null=True,
                             max_length=255, unique=True)
    description = MartorField(blank=True, null=True)
    tags = models.CharField(blank=True, null=True, max_length=255)
    renderer = models.CharField(blank=True, null=True, max_length=512)
    links = models.ManyToManyField('self',
                                   symmetrical=False,
                                   through='ElementLink',
                                   through_fields=('node', 'sibbling'))

    @classmethod
    def cast(cls, element, raise_exception=False):
        child_field_name = cls.__element_related_name__ or cls.__name__.lower()
        if raise_exception:
            return getattr(element, child_field_name)
        return getattr(element, child_field_name, None)

    @classmethod
    def defines(cls, element):
        child_field_name = cls.__element_related_name__ or cls.__name__.lower()
        return hasattr(element, child_field_name)

    def __str__(self):
        return str(self.uid)


class Permissions(IntFlag):
    none = 0
    x = 1
    w = 2
    r = 4
    rw = 6
    all_access = 7


class PermissionsShift(IntEnum):
    u = 6
    g = 3
    a = 0


class ElementMetadata(models.Model):
    element = models.OneToOneField(
        Element, on_delete=models.CASCADE, related_name='metadata')
    created_on = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='created_elements')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL,
                              null=True, blank=True, related_name='owned_elements')
    group = models.ForeignKey(
        Group, on_delete=models.SET_NULL, blank=True, null=True)
    # unix style binary permissions (u+rwx g+rwx a+rwx)
    permissions = models.PositiveSmallIntegerField()

    def __str__(self):
        return str(self.element)

    def get_user_permissions(self, user):
        if user.is_superuser:
            return Permissions.all_access
        scope = PermissionsShift.a
        if self.group is None or user.groups.filter(id=self.group.id).exists():
            scope = PermissionsShift.g
        if self.owner is None or user == self.owner:
            scope = PermissionsShift.u
        return self.get_scope_permission(scope)

    def get_scope_permission(self, scope):
        permission_mask = (0b111 << scope)
        return (self.permissions & permission_mask) >> scope

    def can(self, user_permissions, permission):
        return True if user_permissions & permission else False

    def can_read(self, user_permissions):
        return self.can(user_permissions, Permissions.r)

    def can_write(self, user_permissions):
        return self.can(user_permissions, Permissions.w)

    def can_execute(self, user_permissions):
        return self.can(user_permissions, Permissions.x)

    def set_scope_permissions(self, permissions, shift, commit=True):
        remove_permissions = ~(
            (Permissions.x | Permissions.r | Permissions.w) << shift)
        new_permissions = permissions << shift
        self.set_permissions(
            (self.permissions & remove_permissions) | new_permissions, commit=commit)

    def set_permissions(self, permissions, commit=True):
        self.permissions = permissions
        if commit:
            self.save(update_fields=['permissions'])


#should be element ?
class ElementHistory(models.Model):
    element = models.ForeignKey(Element, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    change = models.CharField(max_length=1024)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.date) + ':' + str(self.element)


class ElementLinkType(models.Model):
    name = models.CharField(max_length=32, unique=True)
    algorithm = models.CharField(max_length=32)

    def __str__(self):
        return self.name

class ElementLink(Element):
    class Meta:
        unique_together = ['node', 'sibbling', 'type']
    node = models.ForeignKey(
        Element, on_delete=models.CASCADE, related_name='link_startpoints')
    sibbling = models.ForeignKey(
        Element, on_delete=models.CASCADE, related_name='link_endpoints')
    type = models.ForeignKey(
        ElementLinkType, on_delete=models.SET_NULL, null=True)
    linked_on = models.DateTimeField(auto_now_add=True)
    alive = models.BooleanField(default=True)

class OffElement(models.Model):
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    content = models.CharField(max_length=4096)
    links = models.ManyToManyField('self',
                                   symmetrical=False,
                                   through='ElementLink',
                                   through_fields=('node', 'sibbling'))

class OffElementLinkType(models.Model):
    class Meta:
        unique_together = ['semantic', 'algorithm']
    semantic = models.CharField(max_length=256, unique=True)
    algorithm = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class OffElementLink(Offlement):
    class Meta:
        unique_together = ['node', 'sibbling', 'type']
    node = models.ForeignKey(
        OffElement, on_delete=models.CASCADE, related_name='link_startpoints')
    sibbling = models.ForeignKey(
        OffElement, on_delete=models.CASCADE, related_name='link_endpoints')
    type = models.ForeignKey(
        OffElementLinkType, on_delete=models.SET_NULL, null=True)
    linked_on = models.DateTimeField(auto_now_add=True)
    alive = models.BooleanField(default=True)

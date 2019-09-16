from off.elements.models import ElementMetadata, ElementHistory, PermissionsShift, Permissions
from off.infrastructure import services as infra
from django.db import transaction
from off.elements.services import element_history, HistoryScope
from off.elements.tools.history import HistoryTransferObject
from off.elements.tools.permissions import get_permissions_rwx

class Services(infra.Services):

    class Preconditions:
        @staticmethod
        def canChangeOwner(user, element):
            return user.is_superuser

        @staticmethod
        def canChangeGroup(user, element):
            if user.is_superuser:
                return True
            return user == element.owner

        @staticmethod
        def canChangePermissions(user, element):
            if user.is_superuser:
                return True
            return user == element.owner

    def __init__(self, context, *args, **kwargs):
        return super().__init__(context, *args, **kwargs)
    
    def __setPropertyHistory(self, element, changes:HistoryTransferObject, property_name, value_from, value_to, value_format):
        with HistoryScope(element, self.user, changes, local_changes_action='set ' + property_name, locals_over_changes=False) as scope:
            scope.changes.addPropertyChange(property_name, value_from, value_to, value_format=value_format)

    @transaction.atomic
    def setOwner(self, metadata:ElementMetadata, new_owner, changes:HistoryTransferObject=None, commit=True):
        if not Preconditions.canChangeOwner(self.user, metadata.element):
            raise PermissionError()
        self.__setPropertyHistory(metadata.element, changes, 'owner', metadata.owner, new_owner, lambda u:u.username)
        metadata.owner = new_owner
        if commit:
            metadata.save(update_fields=['owner'])
        return metadata

    @transaction.atomic
    def setGroup(self, metadata:ElementMetadata, new_group, changes:HistoryTransferObject=None, commit=True):
        if not self.Preconditions.canChangeGroup(self.user, metadata.element):
            raise PermissionError()
        self.__setPropertyHistory(metadata.element, changes, 'group', metadata.group, new_group, lambda g:g.name)
        metadata.group = new_group
        if commit:
            metadata.save(update_fields=['group'])
        return metadata

    @transaction.atomic
    def setPermissions(self, metadata:ElementMetadata, new_permissions, changes:HistoryTransferObject=None, commit=True):
        if not self.Preconditions.canChangePermissions(self.user, metadata.element):
            raise PermissionError()
        self.__setPropertyHistory(metadata.element, changes, 'permissions', metadata.permissions, new_permissions, get_permissions_rwx)
        metadata.set_permissions(new_permissions, commit)
        return metadata

    @transaction.atomic
    def setGroupPermissions(self, metadata:ElementMetadata, new_permissions, changes:HistoryTransferObject=None, commit=True):
        return self.setScopePermissions(metadata, new_permissions, PermissionsShift.g, 'group', changes, commit)

    @transaction.atomic
    def setUserPermissions(self, metadata:ElementMetadata, new_permissions, changes:HistoryTransferObject=None, commit=True):
        return self.setScopePermissions(metadata, new_permissions, PermissionsShift.u, 'user', changes, commit)

    @transaction.atomic
    def setAllPermissions(self, metadata:ElementMetadata, new_permissions, changes:HistoryTransferObject=None, commit=True):
        return self.setScopePermissions(metadata, new_permissions, PermissionsShift.a, 'all', changes, commit)

    @transaction.atomic
    def setScopePermissions(self, metadata:ElementMetadata, new_permissions, scope, scope_name, changes:HistoryTransferObject=None, commit=True):
        if not self.Preconditions.canChangePermissions(self.user, metadata.element):
            raise PermissionError()
        if new_permissions > Permissions.all_access:
            raise ValueError('scope permissions cannot be greater than 7')
        self.__setPropertyHistory(metadata.element, changes, scope_name + ' permissions', metadata.permissions, new_permissions, lambda p: get_permissions_rwx(p, scope))
        metadata.set_scope_permissions(new_permissions, scope, commit)
        return metadata
    
    @staticmethod
    def createElementMetadata(element, created, permissions):
        if created:
            ElementMetadata.objects.create(element=element, permissions=permissions)

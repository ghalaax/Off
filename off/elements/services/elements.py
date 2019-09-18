from django.db import transaction
from off.infrastructure import services as infra
from off.elements.models import (
    Element,
    ElementHistory,
    ElementLink,
    ElementLinkType,
    ElementMetadata,
    PermissionsShift    
)
from off.elements.services import element_metadatas, element_histories, HistoryScope
from off.elements.tools.history import HistoryTransferObject

class Services(infra.Services):
    def __init__(self, context, *args, **kwargs):
        return super().__init__(context, *args, **kwargs)
    
    def __getHistoryScope(self, element=None, changes=None, local_changes_action=None, local_changes=None):
        return HistoryScope(element=element, 
                            user=self.user, 
                            changes=changes, 
                            local_changes=local_changes, 
                            local_changes_action=local_changes_action)

    @transaction.atomic
    def chown(self, element:Element, user, changes:HistoryTransferObject=None, commit=True):
        with self.__getHistoryScope(element, changes, local_changes_action='chown') as scope:
            metadata = element_metadatas.Services(self.context)
            metadata.setOwner(element.metadata, user, scope.changes, commit)
        return element

    @transaction.atomic
    def chgrp(self, element:Element, group, changes:HistoryTransferObject=None, commit=True):
        with self.__getHistoryScope(element, changes, local_changes_action='chgrp') as scope:
            metadata = element_metadatas.Services(self.context)
            metadata.setGroup(element.metadata, group, scope.changes, commit)
        return element

    @transaction.atomic
    def chmod(self, element:Element, permissions, changes:HistoryTransferObject=None, commit=True):
        with self.__getHistoryScope(element, changes, local_changes_action='chmod') as scope:
            metadata = element_metadatas.Services(self.context)
            metadata.setPermissions(element.metadata, permissions, scope.changes, commit)
        return element

    @transaction.atomic
    def chmoduga(self, element:Element, user_permissions, group_permissions, all_permissions, changes:HistoryTransferObject=None, commit=True):
        permissions = (user_permissions << PermissionsShift.u) |\
                      (group_permissions << PermissionsShift.g) |\
                      (all_permissions << PermissionsShift.a) 
        return self.chmod(element, permissions, changes, commit)
    
    @transaction.atomic
    def chmodu(self, element:Element, permissions, changes:HistoryTransferObject=None, commit=True):
        with self.__getHistoryScope(element, changes, local_changes_action='chmod user') as scope:
            metadata = element_metadatas.Services(self.context)
            metadata.setUserPermissions(element.metadata, permissions, scope.changes, commit)
        return element
    
    @transaction.atomic
    def chmodg(self, element:Element, permissions, changes:HistoryTransferObject=None, commit=True):
        with self.__getHistoryScope(element, changes, local_changes_action='chmod group') as scope:
            metadata = element_metadatas.Services(self.context)
            metadata.setGroupPermissions(element.metadata, permissions, scope.changes, commit)
        return element
    
    @transaction.atomic
    def chmoda(self, element:Element, permissions, changes:HistoryTransferObject=None, commit=True):
        with self.__getHistoryScope(element, changes, local_changes_action='chmod all') as scope:
            metadata = element_metadatas.Services(self.context)
            metadata.setAllPermissions(element.metadata, permissions, scope.changes, commit)
        return element
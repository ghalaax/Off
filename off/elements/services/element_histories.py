from django.db import transaction
from off.elements.models import ElementHistory, Element
from off.infrastructure import services as infra
from off.elements.tools.history import HistoryTransferObject

class Services(infra.Services):

    def __init__(self, context, *args, **kwargs):
        return super().__init__(context, *args, **kwargs)

    @transaction.atomic
    def createEntry(self, element: Element, changes: HistoryTransferObject):
        return ElementHistory.objects.create(element=element,
                                             change=str(changes),
                                             author=self.user)
class HistoryScope:
    def __init__(self,  element=None,
                 user=None,
                 changes: HistoryTransferObject = None,
                 local_changes: HistoryTransferObject = None,
                 local_changes_action: str = None,
                 locals_over_changes=True):
        if not local_changes:
            can_create_local = (not changes or locals_over_changes)
            if can_create_local and local_changes_action:
                local_changes = HistoryTransferObject()
                local_changes.setAction(local_changes_action)
            elif not changes:
                raise ValueError(
                    'changes, local_changes or local_changes_action must be given.')
        self.user = user
        self.element = element
        self.commit_changes = True
        if changes:
            self.changes = changes
            self.changes.addEntry(local_changes)
            self.commit_changes = False
        if self.commit_changes:
            if self.element is None:
                raise ValueError('element must be given to commit the changes')
            if self.user is None:
                raise ValueError('user must be given to commit the changes')
        if local_changes:
            self.changes = local_changes

    def __enter__(self):
        return self

    def __exit__(self, ex_type, value, traceback):
        if self.commit_changes:
            services = Services(infra.ServiceContext(self.user))
            services.createEntry(self.element, self.changes)

from off.infrastructure import services as infra
from off.elements.services import element_metadatas, elements as elements_services, element_histories
from off.forums.models import Forum
from django.contrib.auth.models import Group
from off.elements.tools.names import get_title_for_element
from off.elements.models import Permissions
from django.db import transaction


class Services(infra.Services):
    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)
        self.metadatas = element_metadatas.Services(context)
        self.elements = elements_services.Services(context)

    @transaction.atomic
    def createForum(self, title: str):
        forum = Forum()
        forum.title = get_title_for_element(title, Forum)
        forum.save() # save to be able to reference it later
        # create a new django group
        group = Group.objects.create(name=forum.title)
        metadata = self.metadatas.createElementMetadata(forum)
        with element_histories.HistoryScope(forum, self.user, local_changes_action='Create Forum') as scope:
            scope.changes.addPropertyChange('title', None, forum.title)
            self.elements.chgrp(forum, group, changes=scope.changes, commit=False)
            self.elements.chmoduga(forum, Permissions.rw, Permissions.rw, Permissions.r, changes=scope.changes, commit=False)
        metadata.save()
        forum.save()
        return forum

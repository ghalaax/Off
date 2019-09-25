from off.infrastructure import services as infra
from off.elements.services import element_metadatas
from off.elements.models import ElementLink, ElementLinkType, Permissions
from off.elements.services import element_histories, HistoryScope, element_metadatas, elements
from off.elements.tools.names import get_title_for_element
from off.elements.tools.history import HistoryTransferObject
from django.db import transaction

PublicLink = 'publiclink'
PrivateLink = 'privatelink'

class LinkNotAllowed(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Services(infra.Services):
    def __init__(self, context, *args, **kwargs):
        self.histories = element_histories.Services(context)
        self.metadatas = element_metadatas.Services(context)
        self.elements = elements.Services(context)
        return super().__init__(context, *args, **kwargs)
    
    @transaction.atomic
    def _createLinkType(self, link_type):
        link_type = link_type.lower()
        return ElementLinkType.objects.create(name=link_type, algorithm=link_type)

    def getLinkType(self, link_type, private=False) -> ElementLinkType:
        visibility = PrivateLink if private else PublicLink
        link_type = '{visibility}:{link_type}'.format(visibility=visibility, link_type=link_type).lower()
        try:
            return ElementLinkType.objects.get(name=link_type)
        except ElementLinkType.DoesNotExist:
            return self._createLinkType(link_type)

    def isPublicLink(self, link_type):
        return link_type.name.startswith(PublicLink)

    @transaction.atomic
    def _createLink(self, link_type, element, to_element):
        title = get_title_for_element('element(%s) link_type(%s) element(%s)' % (element.uid, link_type.name, to_element.uid), ElementLink)
        link = ElementLink.objects.create(title=title, node=element, sibling=to_element, type=link_type)
        metadata = self.metadatas.createElementMetadata(link)
        with element_histories.HistoryScope(link, self.user, local_changes_action='Create link(%s)' % link_type.name) as scope:
            if self.isPublicLink(link_type):
                self.elements.chmoduga(link, Permissions.rw, Permissions.r, Permissions.r, changes=scope.changes, commit=False)
            else:
                self.elements.chmodu(link, Permissions.rw, changes=scope.changes, commit=False)
        metadata.save()
        link.save()
        return link


    def can_user_link_elements(self, *elements):
        first = True
        can_link = True
        for element in elements:
            if first:
                can_link &= element_metadatas.Preconditions.canRead(self.user, element)
                first = False
            else:
               can_link &= element_metadatas.Preconditions.canWrite(self.user, element) 
            if not can_link:
                break
        return can_link

    @transaction.atomic
    def link(self, element, to_element, link_type, private=False):
        if not self.can_user_link_elements(element, to_element):
            raise PermissionError()
        link_type = self.getLinkType(link_type, private=private)
        try:
            link = ElementLink.objects.get(type=link_type, node=element, sibling=to_element)
            if not link.alive:
                link.alive = True
                link.save()
            return link
        except:
            with HistoryScope(to_element, self.user, local_changes_action='link') as scope:
                link = self._createLink(link_type, element, to_element)
                scope.changes.addEntry('link(%s) with element(%s)' % (link_type.name, element.uid))
                return link
            
        



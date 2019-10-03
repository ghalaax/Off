from django.db import transaction

from off.elements.constants import BuiltinSemantics, source_element_uid
from off.elements.models import Element, ElementLink
from off.infrastructure import services as infra

from ..services import element_notifier


class Services(infra.Services):

    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)
        self.source_element = None
        self.verb_builtin_element = None
        self.__ensure_semantics_builtins__()

    def __ensure_semantics_builtins__(self):
        builtin_semantics = set([b.value for b in BuiltinSemantics])
        builtins_elements = Element.objects.filter(
            uid__in=builtin_semantics).all()
        missing_builtins = builtin_semantics.difference(
            set([b.uid for b in builtins_elements]))
        self.__create_missing_semantic_builtins__(
            [BuiltinSemantics(b) for b in missing_builtins])

    @transaction.atomic
    def __create_missing_semantic_builtins__(self, missing_builtins):
        for builtin in missing_builtins:
            element = self.__create_builtin_element__(builtin)

    @transaction.atomic
    def link_to_element(self, subject_element, link_elements, object_element) -> ElementLink:
        """
        Creates or expands the link between 2 elements with the given link_elements:
         * link_elements: can be an Element list or a single Element
        """
        (link, created) = ElementLink.objects.get_or_create(subject=subject_element,
                                                            object=object_element)
        if isinstance(link_elements, Element):
            link_elements = [link_elements]
        link.links.add(*link_elements)
        link.save()
        if created:
            element_notifier.push(link, self.context)
        return link

    def get_souls(self, elements):
        if not isinstance(elements, list, set, tuple):
            elements = set(elements)
        self.source_element = self.get_source_element()
        return ElementLink.objects.filter(subject=source_element, object__in=elements).all()

    def get_shape(self, element):
        self.source_element = self.get_source_element()
        return Element.objects.get(links__object=BuiltinSemantics.shapes, link_startpoint__subject=self.source_element, link_startpoint__object=element)

    def get_source_element(self) -> Element:
        """
        Gets or creates the source.
        The source shapes itself
        """
        if not self.source_element:
            (self.source_element, created) = self.__create_source_element__()
            if created:
                shapes = self.__get_builtin__(BuiltinSemantics.shapes)
                self.link_to_element(self.source_element,
                                     shapes, self.source_element)
                element_notifier.push(self.source_element)
        return self.source_element

    def get_element(self, **kwargs):
        """
        Gets an element given the kwargs
         * Throws Element.DoesNotExist
        """
        return Element.objects.get(**kwargs)

    @transaction.atomic
    def __create_source_element__(self) -> Element:
        return self.__create_element__(uid=source_element_uid)

    @transaction.atomic
    def __create_element__(self, **kwargs) -> Element:
        return Element.objects.get_or_create(**kwargs)

    @transaction.atomic
    def __create_builtin_element__(self, builtin) -> Element:
        element = self.__create_element__(uid=builtin.value)
        if builtin == BuiltinSemantics.verb:
            self.verb_builtin_element = builtin
        elif not self.verb_builtin_element:
            self.verb_builtin_element = self.__get_builtin__(
                BuiltinSemantics.verb, create_when_needed=True)
        self.source_element = self.get_source_element()
        self.link_to_element(self.source_element,
                             self.verb_builtin_element, element)
        element_notifier.push(element, self.context)
        return element

    def __get_builtin__(self, builtin, create_when_needed=True) -> Element:
        try:
            return Element.objects.get(uid=builtin.value)
        except Element.DoesNotExist:
            if create_when_needed:
                builtin_element = self.__create_builtin_element__(builtin)
                return builtin_element
            return None

    def get_builtin(self, builtin):
        """
        Gets the builtin element matching the given builtin object.

        Returns None if it doesn't exist
        """
        return self.__get_builtin__(builtin, create_when_needed=False)

    @transaction.atomic
    def create_element(self, shape_element, data) -> Element:
        self.source_element = self.get_source_element()
        element = self.__create_element__(data=data)
        self.link_to_element(self.source_element, shape_element, element)


a = {
    'uuid': 'uuid2',
    'content': 'user',
    'links_endpoints': [{
        'uuid': 'uuid2_instanciation',
        'subject': Element('source'),
        'object': Element('uuid2'),
        'links': [{
            'uuid': 'uuid2_shape',
            'subject': Element('uuid2_instanciation'),
            'object': Element('uuid_user')
        }]
    }],
    'links': [{
        'uuid': 'uuid1',
        'subject': Element('uuid2'),
        'object': Element('uuid3'),
        'links': [{
            'uuid': 'uuid1.1',
            'subject': Element('uuid1'),
            'object': Element('semantic_uuid_creates')
        }, {
            'uuid': 'uuid4',
            'subject': Element('uuid1'),
            'object': Element('semantic_uuid_shares'),
            'links': [{
                    'uuid': 'uuid6',
                    'subject': Element('uuid5'),
                    'object': Element('allows_read'),
                    'links': [{
                        'uuid': 'uuid5',
                        'subject': Element('uuid4'),
                        'object': Element('uuid1_shared_to'),  # non semantic
                    }]
            }, {
                'uuid': 'uuid6',
                'subject': Element('uuid5'),
                'object': Element('allows_write'),
                'links': [{
                        'uuid': 'uuid7',
                        'subject': Element('uuid6'),
                        'object': Element('uuid2_shared_to')
                }]
            }]
        }]
    }]
}

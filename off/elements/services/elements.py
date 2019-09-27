import enum
import uuid
import rx
from rx import subject
from rx import operators as ops
import abc

from off.elements.models import Element, ElementLink, Linker, UserElement
from off.elements.services import user_elements
from off.infrastructure import services as infra
from django.db import transaction
from ..services import element_notifier, element_divers


class BuiltinSemantics(enum.Enum):
    verb = uuid.UUID(int=1)
    shapes = uuid.UUID(int=2)
    creates = uuid.UUID(int=3)
    shares = uuid.UUID(int=4)
    allows_read = uuid.UUID(int=6)
    allows_write = uuid.UUID(int=7)
    references = uuid.UUID(int=8)
    changes = uuid.UUID(int=9)
    continues = uuid.UUID(int=10)

    def __str__(self):
        return repr(self)


class Services(infra.Services):
    source_element_uid = uuid.UUID(int=0)

    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)
        self.user_element_services = user_elements.Services.fromContext(
            context)
        self.source_element = None
        self.verb_builtin_element = None
        self.__ensure_semantics_builtins__()

    # todo
    def __ensure_semantics_builtins__(self):
        builtin_semantics = set([b.value for b in BuiltinSemantics])
        builtins_elements = Element.objects.filter(
            uid__in=builtin_semantics).all()
        missing_builtins = builtin_semantics.difference(
            set([b.uid for b in builtins_elements]))
        self.__create_missing_semantic_builtins__(
            [BuiltinSemantics(b) for b in missing_builtins])

    # todo
    @transaction.atomic
    def __create_missing_semantic_builtins__(self, missing_builtins):
        for builtin in missing_builtins:
            element = self.__create_builtin_element__(builtin)

    @transaction.atomic
    def link_to_element(self, subject_element, link_elements, object_element) -> ElementLink:
        (link, created) = ElementLink.objects.get_or_create(subject=subject_element,
                                                            object=object_element)
        if isinstance(link_elements, Element):
            link_elements = [link_elements]
        link.links.add(*link_elements)
        link.save()
        if created:
            element_notifier.push(link, self.context)
        return link

    def get_source_element(self) -> Element:
        if not self.source_element:
            try:
                self.source_element = self.Element.objects.get(
                    uid=self.source_element_uid)
            except Element.DoesNotExist:
                self.source_element = self.__create_source_element__()
                shapes = self.__get_builtin__(BuiltinSemantics.shapes)
                self.link_to_element(source_element, shapes, source_element)
                element_notifier.push(self.source_element)
        return self.source_element

    @transaction.atomic
    def __create_source_element__(self) -> Element:
        return self.__create_element__(uid=self.source_element_uid)

    @transaction.atomic
    def __create_element__(self, **kwargs) -> Element:
        return Element.objects.create(**kwargs)

    @transaction.atomic
    def __create_builtin_element__(self, builtin) -> Element:
        element = self.__create_element__(
            content=str(builtin), uid=builtin.value)
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
            return Element.objects.get(uid=builtin.value, content=str(builtin))
        except Element.DoesNotExist:
            if create_when_needed:
                builtin_element = self.__create_builtin_element__(builtin)
                return builtin_element
            return None

    @transaction.atomic
    def create_element(self, shape, content) -> Element:
        user_element = self.user_element_services.get_user_element()

    def __dive_links__(self, element_link):
        pass

    def can_read(self, element) -> Element:
        user_element = self.user_element_services.get_user_element()
        try:
            direct_link = ElementLink.objects.get(
                subject=user_element, object=element)

        except ElementLink.DoesNotExist:
            pass


def register_diver(diver):
    """
    Register the diver function.
    The diver signature is: func(element, diver_element, target_element)
    """
    def _decorator(func):
        if diver not in element_divers:
            element_divers[diver] = set()
        element_divers[str(diver)].add(func)
        return func
    return _decorator


@register_diver(BuiltinSemantics.creates)
def has_created(creator_element, diver_element: Element, target_element):
    return ElementLink.objects.filter(subject=creator_element, object=target_element, links__object=diver_element).exists()


@register_diver(BuiltinSemantics.shapes)
def get_shape(source_element, diver_element: Element, target_element):
    return Element.objects.get(links__object=diver_element, links_startpoints=source_element, links_endpoints=target_element)


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

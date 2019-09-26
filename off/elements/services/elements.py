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
from ..services import element_notifier


class BuiltinSemantics(enum.Enum):
    verb = uuid.UUID(int=1)
    shapes = uuid.UUID(int=2)
    creates = uuid.UUID(int=3)
    shares = uuid.UUID(int=4)
    allows_read = uuid.UUID(int=5)
    allows_write = uuid.UUID(int=6)
    forbids = uuid.UUID(int=7)
    gives = uuid.UUID(int=8)

    def __str__(self):
        return repr(self)


class Services(infra.Services):
    source_element_uid = uuid.UUID(int=0)

    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)
        self.user_element_services = user_elements.Services.fromContext(
            context)
        self.source_element = None
        self.verb_builtin_element = self.__get_builtin__(BuiltinSemantics.verb,
                                                         create_when_needed=False)
        self.__ensure_semantics_builtins__()

    # todo
    def __ensure_semantics_builtins__(self):
        builtin_semantics = set([b.value for b in BuiltinSemantics])
        builtins_elements = Element.objects.filter(uid__in=builtin_semantics).all()
        missing_builtins = builtin_semantics.difference(
            set([b.uid for b in builtins_elements]))
        self.__create_missing_semantic_builtins__([BuiltinSemantics(b) for b in missing_builtins])

    # todo
    @transaction.atomic
    def __create_missing_semantic_builtins__(self, missing_builtins):
        for builtin in missing_builtins:
            element = self.__create_builtin_element__(builtin)

    @transaction.atomic
    def link_to_element(self, subject_element, verb, object_element) -> ElementLink:
        (link, created) = ElementLink.objects.get_or_create(subject=subject_element,
                                                            object=object_element)
        link.links.add(verb)
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
        element = self.__create_element__(content=str(builtin), uid=builtin.value)
        if builtin == BuiltinSemantics.verb:
            self.verb_builtin_element = builtin
        elif not self.verb_builtin_element:
            self.verb_builtin_element = self.__get_builtin__(BuiltinSemantics.verb, create_when_needed=True)
        self.source_element = self.get_source_element()
        self.link_to_element(self.source_element, self.verb_builtin_element, element)
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
    def create_element(self, element_algorithm, content) -> Element:
        user_element = self.user_element_services.get_user_element()

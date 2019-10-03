from off.elements.models import ElementLink, Element
from ..services import element_divers
from off.elements.constants import BuiltinSemantics


def register_diver(pearl, get_pearl_uid=None):
    """
    Register the diver function.
    The diver signature is: func(element, diver_element, target_element)
    """
    def _decorator(func):
        get_pearl_uid = get_pearl_uid or (lambda p: p.value)
        pearl_uid = get_pearl_uid(pearl)
        if pearl not in element_divers:
            element_divers[pearl_uid] = set()
        element_divers[pearl_uid].add(func)
        return func
    return _decorator


@register_diver(BuiltinSemantics.creates)
def has_created(creator_element, diver_element: Element, target_element):
    return ElementLink.objects.filter(subject=creator_element, object=target_element, links__object=diver_element).exists()


@register_diver(BuiltinSemantics.shapes)
def get_shape(source_element, diver_element: Element, target_element):
    return Element.objects.get(links__object=diver_element, links_startpoints=source_element, links_endpoints=target_element)


class ElementDiver:

    def __dive_links__(self, element_link):
        pass

    def __get_diver_element__(self, diver):
        return None

    def dive(self, source_element, diver, target_element):
        return None

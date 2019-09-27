from .notifications import ElementNotifier


def __get_element_notifier__() -> ElementNotifier:
    if element_notifier:
        return element_notifier
    return ElementNotifier.instance()


element_notifier = __get_element_notifier__()
element_divers = dict()

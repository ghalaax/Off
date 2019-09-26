import abc
import rx
from rx import subject, operators as ops


class PushInterface(abc.ABC):
    @abc.abstractmethod
    def push(self, element, context):
        pass


class NotifierInterface(abc.ABC):
    @abc.abstractmethod
    def get(self) -> rx.Observable:
        pass


class Notification:
    def __init__(self, element, context):
        self.element = element
        self.context = context

    @property
    def e(self):
        return self.element

    @property
    def c(self):
        return self.context


class NotificationManager(PushInterface, NotifierInterface):
    _instance = None

    @classmethod
    def instance(cls) -> cls:
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self, *args, **kwargs):
        self._observable = subject.Subject()

    def push(self, element, context):
        self._observable.on_next(Notification(element, context))

    def get(self, of_type) -> rx.Observable:
        if of_type:
            return self._observable.pipe(
                ops.filter(lambda n: isinstance(n.e, of_type)))
        return self._observable


class ElementNotifier(NotificationManager):
    def get(self, of_type=Element):
        return super().get(of_type=of_type)

import pickle
import pickletools


class ElementDataShaperManager:
    _instance = None

    def __init__(self, *args, **kwargs):
        self.shapers = dict()
        self.default_shaper = ElementDataShaper()
        self.default_shaper_set = {self.default_shaper}

    @classmethod
    def instance(cls) -> ElementDataShaperManager:
        if not cls._instance:
            cls._instance = ElementDataShaperManager()
        return cls._instance

    def __ensure_shape__(self, shape):
        if not hasattr(shape, 'value'):
            raise ValueError('shape must have a value property')

    def register_data_shaping(self, shaper, shape):
        self.__ensure_shape__(shape)
        if shape not in self.shapers:
            self.shapers[shape.value] = set()
        self.shapers[shape.value].add(shaper() if callable(shaper) else shaper)

    def get_shapers(self, shape):
        self.__ensure_shape__(shape)
        return list(self.shapers.get(shape.value, self.default_shaper_set))


class ElementDataShaper:
    def get_data(self, obj):
        return pickle.dumps(obj)

    def get_obj(self, data):
        if not data:
            return None
        return pickle.loads(data)

    def name(self):
        return 'element_default_shaper'

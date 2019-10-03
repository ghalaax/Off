from off.perceptions.tools.data_shaper import ElementDataShaperManager


element_data_shapers = ElementDataShaperManager.instance()


def register_data_shaping(shape):
    def _decorator(cls):
        element_data_shapers.register_data_shaping(cls, shape)
        return cls
    return _decorator

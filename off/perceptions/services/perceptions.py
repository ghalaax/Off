from off.infrastructure import services as infra


class Services(infra.Services):
    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)

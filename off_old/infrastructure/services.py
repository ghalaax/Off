


class Services:
    """
    Base class for services
    Expects a `context` argument having fields:
        * user (the user using the services)
    """
    def __init__(self, context, *args, **kwargs):
        self.context = context
        self.user = context.user

class ServiceContext:
    def __init__(self, user):
        self.user = user


class Services:
    """
    Base class for services
    Expects a `context` argument having fields:
        * user (the user using the services)
    """

    def __init__(self, context, *args, **kwargs):
        self.context = context
        self.user = context.user

    @classmethod
    def fromRequest(cls, request):
        return cls.fromValues(user=request.user)

    @classmethod
    def fromValues(cls, user):
        context = _ServiceContext(user=user)
        return cls.fromContext(context)

    @classmethod
    def fromContext(cls, context):
        return cls(context)


class _ServiceContext:
    def __init__(self, user):
        self.user = user

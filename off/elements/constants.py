import uuid
import enum
source_element_uid = uuid.UUID(int=0)


class BuiltinSemantics(enum.Enum):
    verb = uuid.UUID(int=1)
    shapes = uuid.UUID(int=2)
    creates = uuid.UUID(int=3)
    shares = uuid.UUID(int=4)
    allows_write = uuid.UUID(int=5)
    references = uuid.UUID(int=6)
    changes = uuid.UUID(int=7)
    continues = uuid.UUID(int=8)

    def __str__(self):
        return repr(self)

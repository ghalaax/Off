from off.infrastructure.plugins.inserts import DataType
from off.elements.models import Element


class ElementPlugin:
    plugin_inserts = []
    plugin_name = None
    allowed_element_types = [Element]
    """
    Defines a plugin taht could be applied to an element
    Ex : element edition, linked element creation
    """
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def can_plug_into(self, request, element):
        return self.__allows_element_type(element)

    def __allows_element_type(self, element):
        if not self.allowed_element_types:
            return True
        return any([t for t in self.allowed_element_types
                    if t.defines(element)])

    def create_insert(self, insert, element):
        if callable(insert):
            insert = insert()
        return insert

    @staticmethod
    def is_insert_acceptable(insert, data_type):
        return insert is not None and insert.data_type == data_type

    def get_inserts(self, element, data_type):
        return [self.create_insert(insert, element)
                for insert in self.plugin_inserts
                if self.is_insert_acceptable(insert, data_type)]

    def get_desired_position(self, element):
        """
        Position resolution will occur as a consensus
        """
        return 1

    def get_plugin_name(self):
        return self.plugin_name or self.__class__.__name__.rstrip('Plugin', '')

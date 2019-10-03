from off.infrastructure import services as infra
from off.elements.constants import BuiltinSemantics
from off.elements.services import elements
from off.elements.models import Element, ElementLink
from django.db import transaction
import uuid


class Services(infra.Services):
    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)
        self.elements_services = elements.Services.fromContext(context)

    @transaction.atomic
    def create_shape(self, shape_uid, shape_data) -> Element:
        """
        Creates a shape
         * links with the source
         * adds the shapes semantic

        If the shape already exists, update element data to shape_data and returns the shape
        """
        (shape, created) = self.elements_services.__create_element__(uid=shape_uid)
        if not created:
            shape.data = shape_data
            shape.save()
        else:
            shape_builtin = self.elements_services.get_builtin(
                BuiltinSemantics.shapes)
            source = self.elements_services.get_source_element()
            self.elements_services.link_to_element(
                source, shape_builtin, shape)
        return shape

    def get_shape(self, shape_uid) -> Element:
        """
        Returns the shape with the given uid
         * Throws Element.DoesNotExist if not found
        """
        return self.elements_services.get_element(uid=shape_uid)

    def shape_element(self, element, shape) -> ElementLink:
        """
        Links an element to a shape
         * Returns the link with the source
        """
        if isinstance(shape, uuid.UUID):
            shape = self.get_shape(shape)
        source = self.elements_services.get_source_element()
        return self.elements_services.link_to_element(source, shape, element)

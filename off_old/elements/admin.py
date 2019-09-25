from django.contrib import admin
from off.elements.models import Element, ElementLinkType, ElementMetadata, ElementHistory, ElementLink

# Register your models here.
admin.site.register(Element)
admin.site.register(ElementMetadata)
admin.site.register(ElementHistory)
admin.site.register(ElementLink)
admin.site.register(ElementLinkType)
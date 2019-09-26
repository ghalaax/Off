from django.db import models
from django.contrib.auth.models import User
from django.db import signals
from martor.models import MartorField
import uuid


class Element(models.Model):
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    content = MartorField(max_length=4096)
    links = models.ManyToManyField('self',
                                   symmetrical=False,
                                   through='ElementLink',
                                   through_fields=('subject', 'object'))
    created_on = models.DateTimeField(auto_now_add=True)
    alive = models.BooleanField(default=True)


# class Linker(Element):
#     class Meta:
#         unique_together = ['semantic', 'algorithm']
#     semantic = models.ForeignKey(Element, on_delete=models.SET_NULL, null=True,
#                                  related_name='semantical_linker')
#     algorithm = models.ForeignKey(Element, on_delete=models.SET_NULL, null=True,
#                                   blank=True, related_name='algorithmical_linker')

#     def __str__(self):
#         return '%s:%s' % (self.semantic.content, self.algorithm.content if self.algorithm else '')


class ElementLink(Element):
    class Meta:
        unique_together = ['subject', 'object']     # , 'link']
    subject = models.ForeignKey(
        Element, on_delete=models.CASCADE, related_name='link_startpoints')
    object = models.ForeignKey(
        Element, on_delete=models.CASCADE, related_name='link_endpoints')
    # link = models.ForeignKey(
    #     Linker, on_delete=models.SET_NULL, null=True, related_name='define_links')


class UserElement(Element):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

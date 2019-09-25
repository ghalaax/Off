from off.infrastructure.tools import types
from off.infrastructure.plugins import register, ElementPlugin
from off.infrastructure.plugins.inserts import ActionPluginInsert
from off.forums.models import Forum
from django.utils.translation import gettext

class UniverseHelper:
    def get_selected(self, request, element_type):
        return self.request.session.get(
            'selected', {}).get(
                types.get_full_name(element_type),
                []
            )

class ShareOnForumInsert(ActionPluginInsert):
    action = 'off.forums:share'
    content = gettext('Partager sur le forum {forum}')
    action_name = gettext('Cette action vous permet de partager sur un forum')

    def get_content(self, **kwargs):
        return self.content.format(forum='...')

    def get_action_name(self, **kwargs):
        return self.action_name

@register
class ShareOnForumPlugin(ElementPlugin):
    plugin_inserts = [ShareOnForumInsert]

    def can_plug_into(self, request, element):
        can_plug = super().can_plug_into(element) 
        return can_plug
        


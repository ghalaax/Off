from django.template.loader import render_to_string
from django.views.generic.base import ContextMixin
import enum


class DataType(enum.IntEnum):
    context = 0
    rendered = 1
    json = 2


class InsertData:

    def __init__(self, data, data_type, plugin_insert, **kwargs):
        self._data = data
        self._data_type = data_type
        self._plugin_insert = plugin_insert

    def get_data(self):
        return self._data

    def get_data_type(self):
        return self._data_type

    def get_plugin_insert(self):
        return self._plugin_insert


class PluginInsert(ContextMixin):
    statics = []
    data_type = DataType.context

    def __init__(self, *args, **kwargs):
        self.element = None
        self.request = None

    def set_element(self, element):
        self.element = element

    def get_statics(self):
        """
        This method should return the static dependencies of the plugin such as:
            * css
            * js
        *.css will be added as <link rel = "stylesheet" [...]/>
        *.js will be added as <script [...] />
        """
        return self.statics

    def get_data_type(self, data):
        return self.data_type

    def to_data(self, data):
        return InsertData(data, self.get_data_type(), self)

    def set_common_context_data(self, context):
        context['element'] = self.element
        context['request'] = self.request
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.set_common_context_data(context)

    def render(self, request=None, **kwargs):
        self.request = request
        return self.get_insert_data(**kwargs)

    def get_insert_data(self, request=None, **kwargs):
        context = self.get_context_data(**kwargs)
        return [self.to_data(context)]


class TemplatePluginInsert(PluginInsert):
    template_name = None
    data_type = DataType.rendered

    def get_insert_data(self, **kwargs):
        context = self.get_context_data(**kwargs)
        return [self.to_data(render_to_string(self.template_name, context))]

class ActionPluginInsert(TemplatePluginInsert):
    template_name = 'plugins/action_element_plugin_insert_template.html'
    content = 'content'
    action = 'action'
    action_name = 'action_name'
    inplace = False

    def get_content(self, **kwargs):
        return self.content

    def get_action(self, **kwargs):
        return self.action
    
    def get_action_name(self, **kwargs):
        return self.action_name
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['content'] = self.get_content(**kwargs)
        context['action'] = self.get_action(**kwargs)
        context['action_name'] = self.get_action_name(**kwargs)
        context['inplace'] = self.inplace

class MultiTemplatePluginInsert(PluginInsert):
    plugins = []
    data_type = DataType.rendered

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instances = None

    def get_plugins(self):
        if plugins:
            return [self.instanciate(p) for p in plugins]
        return []

    def instanciate(self, plugin):
        if callable(plugin):
            return plugin()
        return plugin

    def get_insert_data(self, **kwargs):
        if not self.instances:
            self.instances = self.get_plugins()
        return [instance.render(request=self.request, **kwargs) for instance in self.instances]

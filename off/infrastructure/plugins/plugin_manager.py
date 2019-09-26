

class PluginManager():
    _instance = None
    @staticmethod
    def instance():
        if not PluginManager._instance:
            PluginManager._instance = PluginManager()
        return PluginManager._instance

    def __init__(self, *args, **kwargs):
        self.plugins_types = []
        self.plugins = None

    def register_plugin(self, plugin_type):
        self.plugins_types.append(plugin_type)

    def _initialize(self):
        self.plugins = [p() for p in self.plugins_types]

    def get_plugins(self, element):
        if not self.plugins:
            self._initalize()
        return [p for p in self.plugins if p.can_plug_into(element)]

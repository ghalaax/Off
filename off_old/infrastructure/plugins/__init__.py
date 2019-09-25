from off.infrastructure.plugins.element_plugin import ElementPlugin
import off.infrastructure.plugins.plugin_manager
import logging

logger = logging.getLogger('plugins')

plugin_manager = plugin_manager.PluginManager.instance()

def register(cls):
    plugin_manager.register_plugin(cls)
    logger.info('registering plugin %s (%s)', cls.__name__, cls.__module__)
    return cls
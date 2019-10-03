"""
WSGI config for prototype project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application as django_wsgi
from .settings import APPS_PLUGINS
import importlib
import logging

logger = logging.getLogger('plugins')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prototype.settings')


def register_plugins(module):
    plugin_module = '{module}.plugins'.format(module=module)
    try:
        importlib.import_module(plugin_module)
    except ModuleNotFoundError as module_not_found:
        logger.error(str(module_not_found))


def get_wsgi_application():
    wsgi = django_wsgi()
    for app in APPS_PLUGINS:
        register_plugins(app)
    return wsgi


application = get_wsgi_application()

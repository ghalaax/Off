from django.conf import settings
from django.utils import timezone 
from django.http import BadHeaderError
from urllib import parse
import datetime

BASE_PAGE = 'base_page'
NOW = 'now'
VERSION = 'version'
SITE_NAME = 'site_name'
QUERY_STRING = 'querystring'
CONTEXT_BUILD_DURATION = 'context_build_duration'
GLOBAL = 'global'
PAGINATION = 'pagination'

class ContextBuilderInitializationError(Exception):
    """ Happens when the used ContextBuilder is not initialized properly """
    def __init__(self):
        self.message = 'context_not_initialized'

class ContextBuilder():
    def __init__(self, request = None):
        self.request = request
        self.reset()

    def reset(self):
        self._started = timezone.now()
        self._context = {
            GLOBAL : {},
            PAGINATION : {}
        }
        self._set_global(BASE_PAGE, getattr(settings, 'BASE_PAGE', 'infrastructure/base.html'))

    def _check_initialized(self):
        if self._context is None:
            raise ContextBuilderInitializationError()

    def _set_global(self, name, value):
        self._context[GLOBAL][name] = value

    def append(self, name, value):
        self._check_initialized()
        self._context[name] = value
        return self

    def append_kw(self, **kwargs):
        return self.append_dict(kwargs)

    def append_dict(self, obj):
        self._check_initialized()
        self._context = {**(self._context), **obj}
        return self

    def get_query_string(self, req):
        params = req.GET.copy()
        if 'page' in params:
            del params['page']
        return parse.urlencode(params)

    def _set_pagination(self, name, value):
        self._context[PAGINATION][name] = value

    def finalize(self, external_context = None, **kwargs):
        self._check_initialized()
        self._set_global(CONTEXT_BUILD_DURATION, (timezone.now() - self._started).total_seconds())
        self._set_global(NOW, timezone.now())
        self._set_global(VERSION, getattr(settings, 'VERSION', 'VERSION'))
        self._set_global(SITE_NAME, getattr(settings, 'SITE_NAME', 'SITE_NAME'))
        if self.request:
            self._set_pagination(QUERY_STRING, self.get_query_string(self.request))
        external_context = kwargs if external_context is None else {**external_context, **kwargs}
        result = self._context
        self._context = None
        if external_context is not None:
            return {**(result), **external_context}
        return result


from django.conf import settings
from django.shortcuts import reverse, NoReverseMatch
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from off.infrastructure.tools import Tools
import urllib
import inspect


class NavItem:
    default_template = 'infrastructure/navitem_template.html'
    nav_context_name = 'nav_url'

    def __init__(self, label, url, 
                navigation_id, url_params_name=None, 
                template=None, perms=[], 
                context_name=None, 
                extra_css_class=None, 
                widget=None, url_args=None, 
                precondition=None,
                *args, **kwargs):
        self.label = label
        self.extra_css_class = extra_css_class
        self.navigation_id = navigation_id
        self.url = url
        self.perms = perms
        self.url_params_name = url_params_name or dict()
        self.template = template or (settings.NAV_TEMPLATE if hasattr(
            settings, 'NAVITEM_TEMPLATE') else self.default_template)
        self.nav_context_name = context_name or self.nav_context_name
        self.widget = widget
        self.url_args = url_args
        self.precondition = precondition

    def _produce_url_context(self, **kwargs):
        if type(self.url_params_name) != dict:
            return [Tools.get_nested_dict_value(kwargs, k) for k in self.url_params_name]
        return dict((k, Tools.get_nested_dict_value(kwargs, v)) for (k, v) in self.url_params_name.items())

    def _get_url(self, url, context):
        if type(context) == dict:
            return reverse(url, kwargs=context)
        else:
            return reverse(url, args=context)

    def _produce_url_args(self, context):
        if not self.url_args:
            return None
        args = dict()
        for (k, v) in self.url_args.items():
            try:
                args[k] = self._get_url(v, context)
            except NoReverseMatch:
                args[k] = v
        return args

    def _produce_url(self, context):
        url_args = self._produce_url_args(context)
        try:
            url = self._get_url(self.url, context)
            if url_args:
                query = urllib.parse.urlencode(url_args)
                return '%s?%s' % (url, query)
            return url
        except NoReverseMatch:
            query =''
            if context:
                query = urllib.parse.urlencode(context)
            if url_args:
                q = urllib.parse.urlencode(url_args)
                query = query + ('&' if query else '') + q
            if query:
                return '%s?%s' % (self.url, query)
            return self.url
    def _validates_precondition(self, request):
        return (not self.precondition) or self.precondition(request)

    def produce(self, request, **kwargs):
        if self._validates_precondition(request) and request.user.has_perms(self.perms):
            url_context = self._produce_url_context(**kwargs)
            context = {
                'settings':settings,
                'request':request,
                self.nav_context_name: self._produce_url(url_context),
                'content': self.widget.render(request, **kwargs) if self.widget else self.label % kwargs,
                'extra_css_class': self.extra_css_class
            }
            rendered_template = get_template(
                self.template).render(context={**kwargs, **context})
            return format_html('{}', mark_safe(rendered_template))
        return ""


class Navigation:
    default_template = 'infrastructure/navigation_template.html'
    navigation_context_name = 'navigation'
    nav_order = None

    def __init__(self, template=None, context_name=None, nav_order=None, extra_css_class=None, *args, **kwargs):
        self.items = dict()
        self.extra_css_class = extra_css_class
        self.template = template or settings.NAV_TEMPLATE if hasattr(
            settings, 'NAV_TEMPLATE') else self.default_template
        self.navigation_context_name = context_name or self.navigation_context_name
        self.nav_order = nav_order or self.nav_order

    def add_item(self, name, item):
        self.items[name] = item

    def produce(self, request, **kwargs):
        if not self.nav_order:
            self.nav_order = self.items.keys()
        else:
            self.nav_order = [i for i in self.nav_order]
            self.nav_order.extend([item for item in self.items.keys() if item not in self.nav_order])
        items = [self.items[item].produce(request, **kwargs) for item in self.nav_order]
        context = {
            self.navigation_context_name: {
                'settings':settings,
                'request':request,
                'items': [i for i in items if i],
                'extra_css_class': self.extra_css_class
            }}
        if not context[self.navigation_context_name]['items']:
            return ""
        rendered_template = get_template(self.template).render(context=context)
        return format_html('{}', mark_safe(rendered_template))


class NavigationMixin:
    navigation_context_name = 'navigation'

    def _get_attributes(self, of_type):
        return Tools.get_attributes(self, of_type)

    def add_navigation_context(self, request, context):
        result = dict()
        navigations = self._get_attributes(Navigation)
        navigation_items = self._get_attributes(NavItem)

        for (item_name, item) in navigation_items.items():
            if not item.navigation_id in navigations:
                navigations[item.navigation_id] = Navigation()
            navigations[item.navigation_id].add_item(item_name, item)

        for (navigation_id, navigation) in navigations.items():
            result[navigation_id] = navigation.produce(request, **context)
        oo = {**{self.navigation_context_name: result}, **context}
        return oo

    def __getattribute__(self, name):
        attr = object.__getattribute__(self, name)
        if name == 'get_context_data' and hasattr(attr, '__call__'):
            def interceptor(*args, **kwargs):
                result = attr(*args, **kwargs)
                return self.get_navigation_context(result)
            return interceptor
        else:
            return attr
        return super().__getattribute__(name)

    def get_navigation_context(self, context):
        return self.add_navigation_context(self.request, context)

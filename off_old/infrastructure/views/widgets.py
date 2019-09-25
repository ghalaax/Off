from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.contrib.staticfiles.storage import staticfiles_storage
from django import forms
from django.utils import formats
from django.shortcuts import render as template_render

class Widget:
    def __init__(self, content, tag, attrs=None, content_attr=None, template_name=None, *args, **kwargs):
        self.content = content
        self.template_name = template_name
        self.attrs = attrs or dict()
        self.content_attr = content_attr
        self.tag = tag

    def join_attrs(self):
        return mark_safe(' '.join([format_html('{}="{}"', key, value) for (key, value) in self.attrs.items()]))

    def render(self, request, **kwargs):
        if self.template_name:
            context = {**{'attrs':self.attrs,
                    'request':request,
                    'content':self.content}, **kwargs}
            return template_render(request, self.template_name, context)
        if self.content_attr:
            return format_html('<{tag} {content_attr}="{content}" {attrs}></{tag}>', tag=self.tag, content=self.content, content_attr=self.content_attr, attrs=self.join_attrs())
        else:
            return format_html('<{tag} {attrs}>{content}</{tag}>', tag=self.tag, content=self.content, attrs=self.join_attrs())

class ImageWidget(Widget):
    def __init__(self, src, title=None, attrs=None, template_name=None, *args, **kwargs):
        attrs = attrs or dict()
        src = staticfiles_storage.url(src)
        if title:
            attrs['alt'] = attrs['title'] = title
        super().__init__(src, 'img', content_attr='src', attrs=attrs, **kwargs)

class ConnectedImageWidget(ImageWidget):
    def __init__(self, src, title=None, attrs=None, template_name=None, connected_class=None, *args, **kwargs):
        self.connected_class = connected_class
        super().__init__(src, title=title, attrs=attrs, template_name=template_name, *args, **kwargs)

    def render(self, request, **kwargs):
        if request.user.is_authenticated:
            if not self.connected_class in self.attrs.get('class', ''):
                self.attrs['class'] = self.attrs.get('class', '') + ' ' + self.connected_class
        else:
            self.attrs['class'] = self.attrs.get('class', '').replace(self.connected_class, '')
        return super().render(request, **kwargs)


class ComboboxWidget(forms.Select):
    template_name = 'infrastructure/combobox.html'

    def format_value(self, value):
        # Copied from forms.Input - makes sure value is rendered properly
        if value == '' or value is None:
            return ''
        if self.is_localized:
            return formats.localize_input(value)
        return str(value)
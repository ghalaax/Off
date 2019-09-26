from django.utils.html import mark_safe
from off.infrastructure.http.utils import get_redirect_url

def create_link(label, url, style="link-style"):
    return mark_safe("<a class=\"{style}\" href=\"{url}\">{label}</a>".format(
        style=style, label=label, url=get_redirect_url(url)))

def append_link(text, label, url, style):
    return mark_safe(text + "&nbsp;" + create_link(label, url, style))
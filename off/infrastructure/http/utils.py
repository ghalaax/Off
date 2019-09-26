from django.shortcuts import resolve_url
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django.urls.exceptions import NoReverseMatch



def redirect(viewname, getdict=None, permanent=False, *args, **kwargs):
    url = get_redirect_url(viewname, getdict, *args, **kwargs)
    return HttpResponsePermanentRedirect(url) if permanent else HttpResponseRedirect(url)

def get_redirect_url(viewname, getdict=None, *args, **kwargs):
    url = viewname
    try:
        url = resolve_url(viewname, *args, **kwargs)
    except NoReverseMatch as _:
        pass
    if getdict:
        query = urllib.parse.urlencode(getdict)
        url = '%s%s%s' % (url, '&' if '?' in url else '?', query)
    return url

from django.contrib.auth import REDIRECT_FIELD_NAME
import urllib.parse
from functools import wraps
from django.conf import settings
from urllib.parse import urlparse
def request_passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request):
                return view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                    (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(
                path, resolved_login_url, redirect_field_name)
        return _wrapped_view
    return decorator


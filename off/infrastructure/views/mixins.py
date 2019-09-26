from off.infrastructure.views.navigation import Navigation, NavItem, NavigationMixin
from off.infrastructure.views.widgets import ImageWidget, ConnectedImageWidget
from django.utils.translation import gettext as _
from off.infrastructure.http.utils import get_redirect_url
from django import forms
from django.conf import settings


class GenericNavigationMixin(NavigationMixin):
    home = NavItem(_('home'), 'home', 'main',
                   widget=ImageWidget('infrastructure/icons/home.svg', _('home'), attrs={'class': 'home'}))
    account = NavItem(_('account'), '', 'main',
                   extra_css_class="account",
                   template="infrastructure/account_navitem_template.html",
                   widget=ConnectedImageWidget('infrastructure/icons/user.png', _('account'), connected_class='connected', attrs={'class': 'account'}))
    


class RedirectNextMixin:
    next_form_arg = 'next'
    cancel_form_arg = 'cancel_url'

    def form_valid(self, form):
        """If the form is valid, redirect to the supplied URL."""
        self.form = form
        return super().form_valid(form)

    def get_initial(self):
        next_url = self.request.GET.get(self.next_form_arg, None)
        return {self.next_form_arg: next_url}

    def get_url_args(self):
        return {}

    def get_default_next_url(self):
        return 'home'

    def get_default_cancel_url(self):
        return 'home'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs) or dict()
        cancel_url = self.request.GET.get(self.cancel_form_arg, None)
        (getdict, args, url_kwargs) = self._get_url_args()
        if cancel_url:
            data['cancel_url'] = get_redirect_url(cancel_url, getdict, *args, **url_kwargs) 
        else:
            data['cancel_url'] = self.request.META.get('HTTP_REFERER', get_redirect_url(self.get_default_cancel_url(), getdict, *args, **url_kwargs))
        return data

    def _get_url_args(self):
        args = self.get_url_args()
        kwargs = self.get_url_args()
        if isinstance(args, list):
            kwargs = {}
        else:
            args = []
        getdict = kwargs.get('getdict')
        return (getdict, args, kwargs)


    def get_success_url(self):
        redirect_name = self.form.data.get(self.next_form_arg)
        (getdict, args, kwargs) = self._get_url_args()
        if redirect_name:
            return get_redirect_url(redirect_name, getdict, *args, **kwargs)
        return get_redirect_url(self.get_default_next_url(), getdict, *args, **kwargs)

class RedirectNextFormMixin(forms.ModelForm):
    next = forms.CharField(widget=forms.HiddenInput(), required=False)
    


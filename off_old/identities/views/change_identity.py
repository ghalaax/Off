from django.views.generic import UpdateView
from off.identities.models import Identity
from django import forms
from off.identities.services import identity_services
from off.infrastructure.views.contextbuilder import ContextBuilder
from django.db import transaction
from django.utils.translation import gettext as _
from off.infrastructure.views.mixins import GenericNavigationMixin, RedirectNextMixin, RedirectNextFormMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator

class IdentityChangeForm(RedirectNextFormMixin):
    class Meta:
        model = Identity
        fields = ['key']

    @transaction.atomic
    def save(self, commit=True):
        identity = identity_services.Services.ChangeKey(
            self.instance,
            self.cleaned_data['key'])
        return identity

    key = forms.CharField(label=_('nfc_key'),
                              widget=forms.TextInput(
        attrs={'placeholder': _('scan_nfc_card'),
                'autocomplete':'off',
               'autofocus': True}),
        error_messages={'unique': _('key_already_exists')}
    )


@method_decorator(permission_required('identity.change_identity'), 'dispatch')
class IdentityChange(SuccessMessageMixin, RedirectNextMixin, UpdateView, GenericNavigationMixin):
    model = Identity
    template_name = 'identities/change_identity.html'
    context_object_name = 'identity'
    form_class = IdentityChangeForm
    slug_field = 'key'
    slug_url_kwarg = 'off_id'
    success_message = _('identity_is_updated')

    def get(self, request, *args, **kwargs):
        self.contextbuilder = ContextBuilder(request)
        return super().get(self, request, args, kwargs)
    
    def get_initial(self):
        next_url = self.request.GET.get('next', None)
        return {'next': next_url, 'key':''}

    def get_context_data(self, **kwargs):
        self.object.refresh_from_db()
        self.contextbuilder.append_dict(super().get_context_data(**kwargs))
        return self.contextbuilder.finalize()

    def get_url_args(self):
        return {'off_id':self.object.key}

    def get_default_next_url(self):
        return 'off.identities:identity'

    def post(self, request, *args, **kwargs):
        self.contextbuilder = ContextBuilder(request)
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

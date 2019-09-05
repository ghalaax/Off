from django.views.generic import CreateView
from django import forms
from off.identity.models import Identity
from django.conf import settings
from off.infrastructure.views.contextbuilder import ContextBuilder
from django.utils.translation import gettext as _
from off.identity.admin import UserCreationForm
from django.shortcuts import redirect
from off.identity.services import identity_services
from off.infrastructure.user import user_services
from django.db import transaction, IntegrityError
from django.contrib.auth.models import User
from off.infrastructure.views.mixins import GenericNavigationMixin, RedirectNextMixin, RedirectNextFormMixin
from off.infrastructure.forms.user import UserCreateForm
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.forms import PasswordResetForm
from smtplib import SMTPRecipientsRefused
from django.utils.safestring import mark_safe

class IdentityLightUserCreationForm(UserCreateForm):
    @transaction.atomic
    def save(self, commit=True):
        nfc_key = identity_services.Services.GenerateUniqueKey()
        user = self._save_user()
        identity = identity_services.Services.CreateIdentity(
            nfc_key, user=user, is_virtual=True)
        return identity

class IdentityCreationForm(IdentityLightUserCreationForm):
    class Meta:
        model = Identity
        fields = ['key']

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.clean_form(**kwargs)

    def clean_form(self, **kwargs):
        has_key = True if kwargs.get('initial', dict()).get('key') else False
        self.fields['key'].widget.attrs['readonly'] = has_key
        self.fields['key'].widget.attrs['autofocus'] = not has_key

    @transaction.atomic
    def save(self, commit=True):
        user = self._save_user()
        identity = identity_services.Services.CreateIdentity(
            self.cleaned_data['key'], user=user)
        return identity

    key = forms.CharField(label=_('nfc_key'),
                          widget=forms.TextInput(
        attrs={'placeholder': _('scan_nfc_card'),
                'autocomplete':'off',
               'autofocus': True}),
        error_messages={'unique': _('key_already_exists')}
    )

class SendRegistrationMailForm(PasswordResetForm):
    from django.template import loader
    from django.core.mail import EmailMultiAlternatives
    def get_users(self, email):
        return User.objects.filter(**{
            '%s__iexact' % User.get_email_field_name(): email,
            'is_active': True,
        })
    def get_email(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        return email_message

class IdentityCreate(SuccessMessageMixin, RedirectNextMixin, CreateView, GenericNavigationMixin):
    model = Identity
    template_name = 'identity/create_identity.html'
    contextbuilder = None
    success_message = _('identity_is_created')
    email_template_name = "identity/emails/registration_email_template.html"
    html_email_template_name = "identity/emails/registration_html_email_template.html"
    subject_template_name = "dentity/emails/registration_email_subject_template.txt"
    
    def get(self, request, *args, **kwargs):
        self.contextbuilder = ContextBuilder(request)
        try:
            key = self.kwargs['key'].lower()
            identity = Identity.objects.get(key=key)
            return redirect('off.identity:update_key', off_id=identity.key)
        except Identity.DoesNotExist:
            pass
        except KeyError:
            pass
        return super().get(self, request, args, kwargs)

    def get_success_message(self, cleaned_data):
        return mark_safe(super().get_success_message(cleaned_data))

    def get_initial(self):
        key = self.kwargs.get('key', '').lower()
        next_url = self.request.GET.get('next', None)
        return {'key': key, 'next': next_url}

    def get_context_data(self, **kwargs):
        self.contextbuilder.append_dict(super().get_context_data(**kwargs))
        return self.contextbuilder.finalize()

    def _is_anonymous_request(self, request):
        return not request.user.is_authenticated

    def get_form_class(self):
        if self._is_anonymous_request(self.request):
            return IdentityLightUserCreationForm
        return IdentityCreationForm

    def get_url_args(self):
        return {'off_id':self.object.key if self.object else self.kwargs.get('key', None)}

    def get_default_next_url(self):
        return 'off.identity:identity'

    def _send_email(self, request):
        opts = {
            'use_https': self.request.is_secure(),
            'email_template_name': self.email_template_name,
            'html_email_template_name': self.html_email_template_name,
            'subject_template_name': self.subject_template_name,
            'request': request,
            'extra_email_context': {'site_name':settings.SITE_NAME, 'identity_key':self.object.key},
        }
        send_mail = SendRegistrationMailForm({'email':self.object.user.email})
        if send_mail.is_valid():
            send_mail.save(**opts)

    def post(self, request, *args, **kwargs):
        self.contextbuilder = ContextBuilder(request)
        response = super().post(request, *args, **kwargs)
        try:
            if self.object:
                self._send_email(request)
        except SMTPRecipientsRefused:
            if self.object:
                identity_services.Services.SetEmailInvalid(self.object)
            pass
        return response

from django.contrib.auth.models import User
from infrastructure.user import user_services
from infrastructure.views.mixins import RedirectNextFormMixin
from django import forms
from django.db import transaction
from django.utils.translation import gettext as _

class UserCreateForm(RedirectNextFormMixin):
    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'email']

    def _save_user(self):
        email = self.cleaned_data['email'] or None
        user = user_services.Services.CreateLightUser(
            self.cleaned_data['lastname'], self.cleaned_data['firstname'], username=None, email=email)
        return user

    @transaction.atomic
    def save(self, commit=True):
        user = self._save_user()
        return user

    def get_user_id(self):
        if not self.instance:
            return None
        if type(self.instance) is User:
            return self.instance.id
        if not self.instance.user:
            return None
        return self.instance.user.id

    def is_valid(self):
        result = super().is_valid()
        if result:
            email = self.cleaned_data['email'] or None
            lastname = self.cleaned_data['lastname']
            firstname = self.cleaned_data['firstname']
            if user_services.Services.emailExists(lastname, firstname, email=email, pk=self.get_user_id()):
                self.add_error('email', _('email_already_exists'))
                self.fields['email'].widget.attrs['value'] = email or user_services.Services.createDefaultUserEmail(lastname, firstname)
                return False
        return result and True

    email = forms.EmailField(label=_('user_email'),
                             widget=forms.TextInput(attrs={'autocomplete':'off'}), required=True)
    lastname = forms.CharField(label=_('user_lastname'),
                               widget=forms.TextInput(attrs={'autofocus': True, 'autocomplete':'off'}))
    firstname = forms.CharField(label=_('user_firstname'),
                                widget=forms.TextInput(attrs={'autocomplete':'off'}))

class UserChangeForm(UserCreateForm):
    def _save_user(self, user):
        email = self.cleaned_data['email'] or None
        user = user_services.Services.UpdateUser(user,
            self.cleaned_data['lastname'], self.cleaned_data['firstname'], username=None, email=email)
        return user


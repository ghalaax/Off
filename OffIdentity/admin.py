from django.contrib import admin
from OffIdentity.models import OffIdentity
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.admin import UserAdmin

# Register your models here.
class OffIdentityAdmin(admin.ModelAdmin):
    list_display = ('key', 'user', 'is_virtual', 'creation_date')


# Register your models here.

class UniqueEmailForm:
    def clean_email(self):
        qs = User.objects.filter(email=self.cleaned_data['email'])
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.count():
            raise forms.ValidationError(
                'That email address is already in use')
        else:
            return self.cleaned_data['email']

class UserChangeForm(UniqueEmailForm, UserChangeForm):
    email = forms.EmailField(required=True)

class UserCreationForm(UniqueEmailForm, UserCreationForm):
    email = forms.EmailField(required=True)

class OffIdentityUserAdmin(UserAdmin):
    # add the email field in to the initial add_user form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')
        }),
    )
    form = UserChangeForm
    add_form = UserCreationForm

admin.site.unregister(User)
admin.site.register(User, OffIdentityUserAdmin)

admin.site.register(OffIdentity, OffIdentityAdmin)

from django.views.generic import DetailView
from off.identities.models import Identity
from off.infrastructure.views.contextbuilder import ContextBuilder
from django.conf import settings
from off.infrastructure.views.mixins import GenericNavigationMixin


class IdentityView(DetailView, GenericNavigationMixin):
    model = Identity
    template_name = 'identities/details.html'
    context_object_name = 'identity'
    contextbuilder = None
    slug_field = 'key'
    slug_url_kwarg = 'off_id'

    def get(self, request, *args, **kwargs):
        return super().get(request, args, kwargs)
    
    def get_queryset(self, queryset=None):
        return self.model.objects.prefetch_related('user', 
        'user__account',  
        'user__account__transaction_debit',
        'user__account__transaction_credit')

    def get_context_data(self, **kwargs):
        self.contextbuilder = ContextBuilder(self.request)
        self.contextbuilder.append_dict(super().get_context_data(**kwargs))
        self.contextbuilder.append('hide_account_dropdown', True)
        return self.contextbuilder.finalize()
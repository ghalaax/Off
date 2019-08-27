from django.views.generic import DetailView
from OffIdentity.models import OffIdentity
from infrastructure.views.contextbuilder import ContextBuilder
from django.conf import settings
from infrastructure.views.mixins import GenericNavigationMixin


class OffIdentityView(DetailView, GenericNavigationMixin):
    model = OffIdentity
    template_name = 'OffIdentity/details.html'
    context_object_name = 'identity'
    contextbuilder = None
    slug_field = 'key'
    slug_url_kwarg = 'off_id'

    def get(self, request, *args, **kwargs):
        self.contextbuilder = ContextBuilder(request)
        return super().get(self, request, args, kwargs)
    
    def get_queryset(self, queryset=None):
        return self.model.objects.prefetch_related('user', 
        'user__offaccount',  
        'user__offaccount__transaction_debit',
        'user__offaccount__transaction_credit')

    def get_context_data(self, **kwargs):
        self.contextbuilder.append_dict(super().get_context_data(**kwargs))
        self.contextbuilder.append('hide_account_dropdown', True)
        return self.contextbuilder.finalize()
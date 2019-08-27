from django import forms
from django.db.models import Q

class FilteredViewMixin():
    filter_form = None
    initial = None

    def __init__(self, *args, **kwargs):
        self.filter = None
        return super().__init__(*args, **kwargs)

    def get_request(self):
        return self.request

    def get_filter(self):
        if self.filter:
            return self.filter
        if self.filter_form:
            self.filter = self.filter_form(self.get_request().GET or self.get_initial())
            return self.filter
        return None

    def create_field_filter(self, field_name, form):
        field_options = form.filter_options.get(field_name, dict())
        lookups = field_options.get('lookup', [field_name])
        conditions = None
        field_data = form.data.get(field_name)
        if not field_data and not isinstance(form.fields[field_name], forms.BooleanField):
            return None
        for lookup in lookups:
            if callable(lookup):
                field_lookup = lookup(field_data)
                if field_lookup is None:
                    continue
                new_condition = Q(**field_lookup)
            else:
                new_condition = Q(**{lookup:field_data})
            if conditions:
                conditions = conditions | new_condition
            else:
                conditions = new_condition
        return conditions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = self.get_filter()
        return context

    def and_filters(self, filters):
        result = None
        for (name, f) in filters:
            if f:
                if result:
                    result = result & f
                else:
                    result = f
        return result

    def get_takeover_filters(self, form_filter, filters):
        return self.and_filters(filter(lambda elt: elt[0] in form_filter.filter_takeover, filters.items()))

    def get_final_filters(self, form_filter, filters):
        final_filters = self.get_takeover_filters(form_filter, filters)
        if final_filters:
            return final_filters
        return self.and_filters(filters.items())

    def apply_filter(self, queryset):
        f = self.get_filter()
        filters = dict()
        for field in f.fields:
            if not field in f.excludes:
                filters[field] = self.create_field_filter(field, f)
        final_filters = self.get_final_filters(f, filters)
        if not final_filters:
            return queryset
        return queryset.filter(final_filters)
    
    def get_initial(self):
        return self.initial

class FilterForm(forms.Form):
    filter_options = dict()
    filter_takeover = []
    excludes = []
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields:
            self.fields[f].required = False

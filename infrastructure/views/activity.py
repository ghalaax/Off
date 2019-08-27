from django.views import View
from django import forms
from django.http import HttpResponseRedirect
from django.http.request import HttpRequest
from infrastructure.tools import Tools
from infrastructure.http.utils import redirect, get_redirect_url
from infrastructure.views.navigation import NavigationMixin, NavItem, Navigation
from django.core import serializers
import urllib

class GenericActivityRecapForm(forms.Form):
    def __init__(self, db_error=None, *args, **kwargs):
        self.db_error = db_error
        super().__init__(*args, **kwargs)
    def is_valid(self):
        result = super().is_valid()
        self.cleaned_data = dict()
        if self.db_error:
            self.add_error(None, self.db_error)
        return not self.db_error and result

class ActivityFailed(Exception):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

class ActivityNavigationMixin(NavigationMixin):
    def intialize_navigation(self, items):
        self.items = items

    def _get_attributes(self, of_type):
        statics = super()._get_attributes(of_type)
        if of_type == NavItem:
            for index, item in enumerate(self.items):
                statics[item['name']] = NavItem(item['label'], item['url'], 'activity_crumbs')
        if of_type == Navigation:
            statics['activity_crumbs'] = Navigation(extra_css_class='activity-crumbs')
        return statics
    
    def get_finalize_parameters(self):
        return dict()

class ActivityParameter:
    json = 'json'
    mode_in = 'in'
    mode_out = 'out'
    mode_inout = 'inout'

    class _jsonserialization:
        @staticmethod
        def serialize(obj):
            if not obj:
                return obj
            return serializers.serialize('json', (obj,))
        @staticmethod
        def deserialize(obj):
            if not obj:
                return obj
            return next(serializers.deserialize("json", obj)).object

    class _anyserialization:
        def __init__(self, data_type, *args, **kwargs):
            self.data_type = data_type
        @staticmethod
        def serialize(obj):
            return obj
        def deserialize(self, obj):
            return self.data_type(obj)

    def __init__(self, data_type, mode=mode_inout, mandatory=True, *args, **kwargs):
        self.serializer = self._jsonserialization() if data_type == self.json else self._anyserialization(data_type)
        self.value = None
        self.mode = mode
        self.is_out = None
        self._mandatory = mandatory
        self.name = None
    
    def copy(self):
        param = ActivityParameter(None)
        param.serializer = self.serializer
        param.value = self.value
        param.mode = self.mode
        param.is_out = self.is_out
        param._mandatory = self._mandatory
        param.name = self.name
        return param

    def is_in_mandatory(self):
        return self._mandatory and self.mode != self.mode_out

    def is_out_mandatory(self):
        return self._mandatory and self.mode != self.mode_in

    def set_out_value(self, obj):
        if self.mode == self.mode_in:
            self.value = None
            return
        if self.is_out_mandatory() and obj == None:
            raise ActivityFailed('Missing out parameter %s' % self.name)
        self.is_out = True
        if obj is not None:
            self.value = self.serializer.serialize(obj)
    def get_out_value(self):
        if self.is_out_mandatory() and self.value == None:
            raise ActivityFailed('Missing out parameter %s' % self.name)
        if self.is_out:
            return self.value
        return self.serializer.serialize(self.value)

    def set_in_value(self, obj):
        if self.mode == self.mode_out:
            self.value = None
            return
        if self.is_in_mandatory() and obj == None:
            raise ActivityFailed('Missing in parameter %s' % self.name)
        self.is_out = False
        if obj is not None:
            self.value = self.serializer.deserialize(obj)
    def get_in_value(self):
        if self.is_in_mandatory() and self.value == None:
            raise ActivityFailed('Missing in parameter %s' % self.name)
        if self.is_out == False:
            return self.value
        return self.serializer.deserialize(self.value)

    def set_param_name(self, name):
        self.name = name

    def get_for_context(self, name = None):
        name = name or self.name
        return {name:self.get_in_value()}
    
    def clear(self):
        self.value = None

class ActivityStep(View):
    activity_step_context_member_name = 'activity_step_context'

    def __init__(self, view_class, *args, **kwargs):
        self.view_class = view_class
        self.activity = None
        self.finalizing = False
        self.name = None

    def get_view(self):
        view = self.view_class()
        params = Tools.get_attributes(view, ActivityParameter)
        for (name, param) in params.items():
            param.clear()
        return view

    def _prepare_post_request(self, request):
        self.view = self.get_view()
        context = self._get_context(request)
        self.view.request = request
        self.view.extra_context = context
        self.view.success_url = self.activity.get_next_step_url(
            self.name, request)
        self._set_parameters(request)
        self._prepare_navigation_context(request)
    
    def _prepare_navigation_context(self, request):
        if issubclass(self.view.__class__, ActivityNavigationMixin):
            crumbs = self.activity.get_navigation_crumbs(self.name, request)
            self.view.intialize_navigation(crumbs)

    def _get_context(self, request):
        context = self.activity.get_existing_context(
            request, self.name) or dict()
        context['previous_activity_step'] = self.activity.get_previous_step(
            self.name)
        context['next_activity_step'] = self.activity.get_next_step(self.name)
        context['cancel_url'] = self.activity.get_cancel_url(request)
        context['activity_title'] = self.activity.title
        context['activity_step_title'] = self.get_activity_step_title()
        return context
    
    def get_activity_step_title(self):
        index = self.activity._get_step_index(self.name)
        return self.activity._get_step_label(self.name, index)

    def _prepare_get_request(self, request):
        self.view = self.get_view()
        context = self._get_context(request)
        self.view.request = request
        self.view.extra_context = context
        self._set_parameters(request)
        self._prepare_navigation_context(request)

    def _set_parameters(self, request):
        params = Tools.get_attributes(self.view, ActivityParameter)
        session_parameters = self.activity.get_parameters(request)
        if not session_parameters:
            return
        for (name, param) in params.items():
            value = session_parameters.get(name)
            param.set_param_name(name)
            param.set_in_value(value)
    
    def _get_parameters(self):
        params = Tools.get_attributes(self.view, ActivityParameter)
        return dict((name, param.get_out_value()) for (name, param) in params.items())

    def get_label(self):
        return getattr(self.view_class, 'crumb_label', '')

    def get(self, request, *args, **kwargs):
        self._prepare_get_request(request)
        result = self.view.get(request, *args, **kwargs)
        return result

    def _after_post_request_hook(self, request):
        ctx = getattr(self.view, self.activity_step_context_member_name, None)
        self.activity.set_context(request, self.name, ctx)
        out = self._get_parameters()
        self.activity.set_parameters(request, out)

    def post(self, request, *args, **kwargs):
        self._prepare_post_request(request)
        response = self.view.post(request, *args, **kwargs)
        if type(response) == HttpResponseRedirect:
            self._after_post_request_hook(request)
            if self.finalizing:
                finalizing_args = self.view.get_finalize_parameters()
                if finalizing_args is dict:
                    return self.activity.finalize(request, **finalizing_args)
                else:
                    return self.activity.finalize(request, *finalizing_args)
        return response


class ActivityView(View):
    steps_order = None
    current_step_url_arg = 'activity_{}_step'
    session_activity_format = 'activity_{}'
    session_activity_finalize = 'activity_next'
    session_activity_cancel = 'activity_cancel_url'
    next_url_arg = 'next'
    cancel_url_arg = 'cancel_url'
    default_next_url = 'home'
    default_cancel_url = 'home'
    activity_parameters_name = 'parameters'
    crumbs_labels = None

    def __init__(self, **kwargs):
        self.name = self.__class__.__name__
        self.setup_activity_steps()
        super().__init__(**kwargs)

    def setup_activity_steps(self):
        self.steps = Tools.get_attributes(self, ActivityStep)
        for (name, view) in Tools.get_attributes(self, View).items():
            self.steps[name] = ActivityStep(view)
        self._initialize_steps()
        self.steps_order = self.steps_order or self.steps().keys()

    def _initialize_steps(self):
        for (name, step) in self.steps.items():
            step.activity = self
            step.name = name
        finalizing_step = self.steps[self.steps_order[-1]]
        finalizing_step.finalizing = True

    def set_context(self, request, name, context):
        self._add_to_session(request, name, context)

    def get_parameters(self, request):
        return self._get_activity_session(request, self.activity_parameters_name)

    def set_parameters(self, request, parameters):
        self._add_to_session(
            request, self.activity_parameters_name, parameters)

    def get_existing_context(self, request, name):
        return request.session[self._get_session_id()].get(name, None)

    def get_current_step(self, request):
        step = request.GET.get(self._get_step_id(), None)
        if not step:
            step = self.steps_order[0]
        return self.steps[step]

    def _get_activity_step_url(self, index):
        name = self.steps_order[index]
        return {self._get_step_id(): name}

    def _get_step_index(self, name):
        return self.steps_order.index(name)

    def get_previous_step(self, name):
        index = self._get_step_index(name)
        return None if index == 0 else self._get_activity_step_url(index - 1)

    def _get_step_label(self, name, index):
        return self.steps[name].get_label() or (self.crumbs_labels[index] if self.crumbs_labels else name)

    def get_navigation_crumb_url(self, index, request):
        parameter = self._get_activity_step_url(index)
        return self.get_url_from_request(request, parameter)

    def get_navigation_crumb(self, name, index, request):
        return {'label':self._get_step_label(name, index),
        'name':name,
        'url':self.get_navigation_crumb_url(index, request)}

    def get_navigation_crumbs(self, name, request):
        index = self._get_step_index(name)
        previouses = self.steps_order[:(index + 1)]
        return [self.get_navigation_crumb(key, index, request) for index, key in enumerate(previouses)]

    def get_next_step(self, name):
        index = self._get_step_index(name)
        return None if name == self.steps_order[-1] else self._get_activity_step_url(index + 1)

    def get_url_from_request(self, request, parameters=None):
        path = request.path
        current_parameters = dict()
        for (key, value) in request.GET.items():
            current_parameters[key] = value
        parameters = {**current_parameters, **parameters} if parameters else current_parameters
        query = urllib.parse.urlencode(parameters)
        if query:
            url = '%s?%s' % (request.path, query)
        else:
            url = request.path
        return url

    def get_next_step_url(self, name, request):
        parameter = self.get_next_step(name)
        return self.get_url_from_request(request, parameter)

    def get_cancel_url(self, request):
        return self._get_activity_session(request, self.session_activity_cancel)

    def finalize(self, request, *args, **kwargs):
        url = self._get_activity_session(request, self.session_activity_finalize)
        self._clear_session(request)
        args = [None, False] + [x for x in args]
        return redirect(url, *args, **kwargs)

    def _get_activity_session(self, request, item):
        return request.session[self._get_session_id()].get(item)

    def _get_session_id(self):
        return self.session_activity_format.format(self.name)

    def _get_step_id(self):
        return self.current_step_url_arg.format(self.name.lower())

    def _clear_session(self, request):
        request.session.pop(self._get_session_id(), None)

    def _add_to_session(self, request, name, value):
        request.session[self._get_session_id()][name] = value
        request.session.modified = True

    def _append_to_session(self, request, name, value):
        request.session[self._get_session_id()][name] = value
        request.session.modified = True

    def _clear_session_if_needed(self, request, step):
        if self.steps_order.index(step.name) == 0:
            self._clear_session(request)

    def _create_session_if_needed(self, request):
        if not self._get_session_id() in request.session:
            request.session[self._get_session_id(
            )] = self._create_default_session(request)

    def _get_cancel_url(self, request):
        return request.GET.get(self.cancel_url_arg, None) or request.META.get('HTTP_REFERER', self.default_cancel_url)

    def _get_finalize_url(self, request):
        return request.GET.get(self.next_url_arg, self.default_next_url)

    def _create_default_session(self, request):
        return {
            self.session_activity_finalize: self._get_finalize_url(request),
            self.session_activity_cancel:self._get_cancel_url(request)
        }

    def _restart_activity(self):
        return redirect(self.get_url_from_request(self.request, {self._get_step_id():self.steps_order[0]}))

    def get(self, request, *args, **kwargs):
        step = self.get_current_step(request)
        self._clear_session_if_needed(request, step)
        self._create_session_if_needed(request)
        try:
            return step.get(request, *args, **kwargs)
        except ActivityFailed as _:
            return self._restart_activity()

    def post(self, request, *args, **kwargs):
        try:
            if not self._get_session_id() in request.session:
                return self._restart_activity()
            return self.get_current_step(request).post(request, *args, **kwargs)
        except ActivityFailed as _:
            return self._restart_activity()

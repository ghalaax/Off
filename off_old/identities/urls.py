"""SipyApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.shortcuts import render
from django.views.generic import RedirectView
from off.identities.views.create_identity import IdentityCreate
from off.identities.views.view_identity import IdentityView
from off.identities.views.change_identity import IdentityChange

app_name = 'off.identities'

urlpatterns = [
    path('create/', IdentityCreate.as_view(), name='create'),
    path('create/<str:key>/', IdentityCreate.as_view(), name='create'),
    path('<str:off_id>/', IdentityView.as_view(), name='identity'),
    path('change/<str:off_id>/', IdentityChange.as_view(), name='update_key')
    #path('base', TemplateView.as_view(template_name="SipyApp/base.html"))
]

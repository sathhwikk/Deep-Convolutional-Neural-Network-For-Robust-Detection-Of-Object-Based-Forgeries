"""Forgery URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path
from UserApp import views
from django.conf import settings
from django.conf.urls.static import static
import os
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index),
    path('User',views.Admin),
    path('Register',views.Register),
    path('RegAction', views.RegAction),
    path('LogAction', views.LogAction),
    path('Home',views.Home),
    path('Detect',views.Detect),
    path('LoadDataset',views.LoadDataset),
    path('ProcessImage', views.ProcessImage),
    path('GenerateModel',views.GenerateModel),
    path('ForgeryDetect',views.Detect),
    path('DetectFAction',views.DetectFAction),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

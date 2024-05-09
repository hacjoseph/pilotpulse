"""
URL configuration for api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include, re_path
from rest_framework import routers

from pilotes.views import PiloteViewSet
from experimentations.views import ExperimentationViewSet

from . import views

from django.conf import settings
from django.conf.urls.static import static



routeur = routers.SimpleRouter()
routeur.register('pilotes', PiloteViewSet, basename='pilotes')
routeur.register('experimentations', ExperimentationViewSet, basename='experimentations')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/pilotes/', include('pilotes.urls')), 
    path('api/experimentations/', include('experimentations.urls')),
    path('fitbit/', include('fitbit.urls')),
    path('api/', include(routeur.urls)),

    re_path('signup', views.signup),
    re_path('login', views.login),
    re_path('test_token', views.test_token),
    re_path('check_authentication', views.check_authentication),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

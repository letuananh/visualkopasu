"""viskosite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from visualkopasu.visko2 import views as visko2_views

urlpatterns = [
    url(r'^$', visko2_views.home, name='visko2_home'),
    url(r'^visko1/', include('visualkopasu.visko1.urls', namespace="visko1"),),
    url(r'^visko2/', include('visualkopasu.visko2.urls', namespace="visko2"),),
    url(r'^visko2/', include('visualkopasu.visko2.urls', namespace="visko2"),),
    url(r'^yawol/', include('yawoldjango.urls', namespace="yawol"),),
    url(r'^admin/', admin.site.urls),
]

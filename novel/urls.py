"""novel URL Configuration

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
from django.urls import path, re_path
from novel import views

urlpatterns = [
    path('ad/min/', admin.site.urls),
    path('', views.home),
    path('jump', views.jump),
    re_path(r'^source/(?P<s>\w+)/(?P<b>\w+)\.html', views.sbc),
    re_path(r'^list(-(?P<type>[a-zA-Z]+))?(-(?P<page>\d+))?\.html$', views.home),
    re_path(r'^book/(?P<pinyin>\w+)\.html', views.book),
    re_path(r'(?P<pinyin>\w+)/chapters\.html', views.chapter_list),

]

handler404 = views.page_not_found
handler500 = views.server_error

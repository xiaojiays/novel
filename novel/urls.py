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
    path('search', views.search),
    re_path(r'^source/(?P<s>\w+)/(?P<b>\w+)\.html', views.sbc),
    re_path(r'^list(-(?P<type>[a-zA-Z]+))?(-(?P<page>\d+))?\.html$', views.home),
    re_path(r'^category(-(?P<page>\d+))?\.html$', views.category_list),
    re_path(r'^category/(?P<pinyin>\w+)(-(?P<page>\d+))?\.html$', views.category_list),
    re_path(r'^book/(?P<pinyin>\w+)\.html', views.book),
    re_path(r'(?P<pinyin>\w+)/chapters(-(?P<page>\d+))?\.html', views.chapter_list),
    re_path(r'^newest(-(?P<page>\d+))?\.html', views.newest),
    re_path(r'^finish(-(?P<page>\d+))?\.html', views.finish),
    re_path(r'^rank(-(?P<type>[a-zA-Z]+))?\.html', views.rank),
    re_path(r'^author/(?P<pinyin>\w+)\.html', views.author_works),
    re_path(r'^trends(-(?P<page>\d+))?\.html', views.trends),
    re_path(r'^subject(-(?P<page>\d+))?\.html', views.subject),
]

handler404 = views.page_not_found
handler500 = views.server_error

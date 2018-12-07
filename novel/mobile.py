from django.shortcuts import render_to_response
from novel import settings


def home(request):
    params = {
        'settings': settings,
    }
    return render_to_response('m/home.html', params)

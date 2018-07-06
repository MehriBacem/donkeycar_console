from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.template import loader
from django.http import HttpResponse
from console.models import *
import requests
import urllib
import json
import os


def github_check(f):
    def wrap(request, *args, **kwargs):
        count1 = github.objects.filter().count()

        if (count1 == 0):
            return HttpResponseRedirect("/settings/")
        return f(request, *args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


def myuser_login_required(f):
        def wrap(request, *args, **kwargs):
            # this check the session if userid key exist, if not it will redirect to login page
            if 'userid' not in request.session.keys():
                return HttpResponseRedirect("/")
            return f(request, *args, **kwargs)

        wrap.__doc__ = f.__doc__
        wrap.__name__ = f.__name__
        return wrap


def myuser_index(f):
    def wrap(request, *args, **kwargs):
        # this check the session if userid key exist, if not it will redirect to login page
        if 'userid'  in request.session.keys():
            return HttpResponseRedirect("/home/")
        return f(request, *args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap

@myuser_index
def index(request):

    template = loader.get_template('console/login.html')
    return HttpResponse(template.render({}, request))


def home(request):

       template = loader.get_template('console/home.html')
       return HttpResponse(template.render({}, request))



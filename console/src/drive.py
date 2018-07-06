
import subprocess
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.template import loader

import subprocess

from django.http import HttpResponse
from console.models import *
from console.views import myuser_login_required




def github_check(f):
    def wrap(request, *args, **kwargs):
        count1 = github.objects.filter().count()

        if (count1 == 0):
            return HttpResponseRedirect("/settings/")
        return f(request, *args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


@myuser_login_required
@github_check
def get_car_status_training(request):
    try:
        poll = proc.poll()
        if poll == None:

            responseCode = 200
            responseMessage = 'Your process is up and running!'
            response = 'Training'
            return HttpResponse(response)
        else:
            responseCode = 604
            responseMessage = 'Your process is down!'
            response = ''

            print(responseMessage)
    except:

        responseMessage = 'Your process is down!'
        response = ''

    return HttpResponse(response)

@myuser_login_required
@github_check
def drive(request):
       try:
            Local_directory = local_directory.objects.latest('id')
            updated_local_directory_name = Local_directory.name
       except:
            updated_local_directory_name = ''
       print(request.POST)
       global proc
       print("hey")
       if 'start' in request.POST:
           print("start")
           try:
               exist_controller = controller.objects.latest('id')
               controller_mode = exist_controller.training
           except:
               controller_mode = ''

           if controller_mode != '':

              proc = subprocess.Popen(["python", "/home/pi/"+updated_local_directory_name+"/manage.py", "drive",controller_mode])
           else:
              proc = subprocess.Popen(["python", "/home/pi/"+updated_local_directory_name+"/manage.py", "drive"])

       # proc = subprocess.Popen(["python", "/home/pi/d2/manage.py", "drive"])

       elif 'stop' in request.POST:
           try:
             proc.kill()
           except:
               print("no proc")


       template = loader.get_template('console/home.html')
       return HttpResponse(template.render({}, request))
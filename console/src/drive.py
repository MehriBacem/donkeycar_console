
import subprocess
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.template import loader

import subprocess

from django.http import HttpResponse
from console.models import *


def credentials_check(f):
    def wrap(request, *args, **kwargs):
        count = credentials.objects.filter().count()
        count1 = github.objects.filter().count()

        if (count != 0 and count1 != 0):
            result = credentials.objects.raw('SELECT * FROM console_credentials LIMIT 1;')
            global AWS_ACCESS_KEY_ID
            global AWS_SECRET_ACCESS_KEY
            AWS_ACCESS_KEY_ID = result[0].aws_access_key_id
            AWS_SECRET_ACCESS_KEY = result[0].aws_secret_access_key
        else:
            return HttpResponseRedirect("/settings/")
        return f(request, *args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap




@credentials_check
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


@credentials_check
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
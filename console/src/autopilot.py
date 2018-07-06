import simplejson as json
from django.http import HttpResponse,HttpResponseRedirect
import json
import requests
from urllib.parse import urlparse
import os.path
import boto3
import subprocess
import os

from django.http import HttpResponse

from console.models import *

from console.views import myuser_login_required
import urllib


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
def autopilot(request):
        id = request.GET.get('id', '')
        facebook_id = request.session['userid']
        try:
            Local_directory = local_directory.objects.latest('id')
            updated_local_directory_name = Local_directory.name
        except:
            updated_local_directory_name = ''

        path = os.popen('echo ~/'+updated_local_directory_name+'/models/').read()
        path = path.split()
        try:
            updated_repo = github.objects.latest('id')
            extension = updated_repo.extension
        except:
            extension = ''
        if extension != '':
            model_name = facebook_id+'_job_' + str(id) + extension
        else:
            model_name = facebook_id+'_job_' + str(id)
        job_name = facebook_id+'job_' + str(id)

        s3_data = {"name": "models/" + model_name}

        url = "https://esx3owu58f.execute-api.us-east-1.amazonaws.com/dev/download/from/S3"
        headers = {'Content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(s3_data), headers=headers)

        response_url = (response.json())['url']

        if (os.path.exists(path[0] + job_name) == True):
            print("it exists")
        else:
            urllib.request.urlretrieve(response_url, path[0] + job_name)

        try:
           exist_controller = controller.objects.latest('id')
           controller_mode = exist_controller.autopilot
        except:
           controller_mode=''

        global autopilot_proc

        autopilot_proc = subprocess.Popen(["python", "/home/pi/"+updated_local_directory_name+"/manage.py", "drive", "--model", "/home/pi/"+updated_local_directory_name+"/models/" + job_name])
        return HttpResponseRedirect('/jobs/')

        #os.system('python ~/d2/manage.py drive --model ~/d2/models/' + model_name)
@myuser_login_required
@github_check
def get_car_status_autopilot(request):
    try:
        poll = autopilot_proc.poll()
        if poll == None:
            responseCode = 200
            responseMessage = 'Your process is up and running!'
            response = 'Autopilot'

        else:
            responseMessage = 'Your process is down!'
            response = ''
    except:
        responseMessage = 'Your process is down!'
        print(responseMessage)
        response = ''

    return HttpResponse(response)
@myuser_login_required
@github_check
def kill_proc(request):
    try:
       autopilot_proc.kill()
    except:
        print("no autopilot ptoc")
    return HttpResponseRedirect('/jobs/')


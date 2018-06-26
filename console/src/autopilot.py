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



@myuser_login_required
@credentials_check
def autopilot(request):
        id = request.GET.get('id', '')
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
            model_name = 'job_' + str(id) + extension
        else:
            model_name = 'job_' + str(id)
        job_name = 'job_' + str(id)
        s3_data = {'AWS_ACCESS_KEY_ID': AWS_ACCESS_KEY_ID, 'AWS_SECRET_ACCESS_KEY': AWS_SECRET_ACCESS_KEY}

        url = "https://fo3dpxzfqh.execute-api.us-east-1.amazonaws.com/dev/downloadFromS3"
        headers = {'Content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(s3_data), headers=headers)

        print(response.json())
        response_url = (response.json())['url']
        o = urlparse(response_url)
        key_path = o.path.split('/', 1)[1]
        s3 = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        if (os.path.exists(path[0] + model_name) == True):
            print("it exists")
        else:
            s3.Object(AWS_ACCESS_KEY_ID.lower(), key_path.split('/', 1)[1] + '/' + model_name).download_file(
                path[0] + job_name)

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
def kill_proc(request):
    try:
       autopilot_proc.kill()
    except:
        print("no autopilot ptoc")
    return HttpResponseRedirect('/jobs/')


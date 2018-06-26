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

def kill_proc(request):
    try:
       autopilot_proc.kill()
    except:
        print("no autopilot ptoc")
    return HttpResponseRedirect('/jobs/')


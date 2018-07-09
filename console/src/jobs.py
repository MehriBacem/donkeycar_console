
import simplejson as json
from django.http import HttpResponse,HttpResponseRedirect

import json
import requests
from urllib.parse import urlparse
import os.path
from django.utils.dateparse import parse_datetime
from datetime import timedelta
from django.template import loader
import pytz
import boto3
import os
from django.http import HttpResponse
from boto.s3.connection import S3Connection
from boto.s3.key import Key
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
def delete_remark(request):
    id= request.GET.get('id', '')
    remarks.objects.filter(id=id).delete()
    return HttpResponseRedirect('/jobs/')


def delete_job(request):
    id= request.GET.get('id', '')
    Jobs.objects.filter(id=id).delete()
    return HttpResponseRedirect('/jobs/')
@myuser_login_required
def add_remark(request):

    job_id =  request.POST['id']
    print(job_id)
    comment = request.POST['var']
    print(comment)
    remark = remarks(remark=comment)
    remark.save()
    job = Jobs.objects.get(id=job_id)
    job.Comments.add(remark)
    return HttpResponse('success')
@github_check
def verify_logs(state,id,facebook_id):

     data = {'id': id,'facebook_id':facebook_id }
     url = "https://j9p3fxvn66.execute-api.us-east-1.amazonaws.com/dev/logs/verify"
     headers = {'Content-type': 'application/json'}
     response = requests.post(url, data=json.dumps(data), headers=headers)

     if json.loads(response.json()['body'])['message'] == "Found":
         url_to_download = json.loads(response.json()['body'])['url_training_log']
         url1_to_download = json.loads(response.json()['body'])['url_commands_log']
         Jobs.objects.filter(id=id).update(log_url=url_to_download)
         Jobs.objects.filter(id=id).update(commands_log_url=url1_to_download)

     else:
         print("not found")




@myuser_login_required
def cancel_request(request):

       id = request.GET.get('id', '')
       job = Jobs.objects.get(id=id)
       instance_id =job.instance_id
       data = {'instance_id': instance_id}
       url = "https://j9p3fxvn66.execute-api.us-east-1.amazonaws.com/dev/request/cancel"
       headers = {'Content-type': 'application/json'}
       response = requests.post(url, data=json.dumps(data), headers=headers)
       if json.loads(response.json()['body'])['result'] == "success":
           Jobs.objects.filter(id=id).update(state='Canceled')
           Jobs.objects.filter(id=id).update(duration='0')
       return HttpResponseRedirect('/jobs/')

@myuser_login_required
def update_status_by_id(request):

        print(request)
        facebook_id = request.session['userid']
        id = request.GET.get('id', '')
        job = Jobs.objects.get(id=id)
        verify_logs(job.state,job.id,facebook_id)

        try:
                    updated_repo = github.objects.latest('id')
                    extension = updated_repo.extension
        except:
                    extension = ''

        if extension != '':
                    model_name = facebook_id+'_job_' + str(job.id) + extension
        else:
                    model_name = facebook_id+'_job_' + str(job.id)
        data = {'model_name': model_name,'facebook_id':facebook_id}
        url = "https://j9p3fxvn66.execute-api.us-east-1.amazonaws.com/dev/job/update"
        headers = {'Content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(data), headers=headers)


        print(response.json())
        return HttpResponseRedirect('/jobs/')



def convert_timedelta(duration):
    days, seconds = duration.days, duration.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    return hours, minutes, seconds

@myuser_login_required
@github_check
def copy_local(request):
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
       s3_data = {"name" : "models/"+model_name}

       url = "https://j9p3fxvn66.execute-api.us-east-1.amazonaws.com/dev/download/from/S3"
       headers = {'Content-type': 'application/json'}
       response = requests.post(url, data=json.dumps(s3_data), headers=headers)

       response_url = (response.json())['url']

       if( os.path.exists(path[0]+model_name) == True ):
         print("it exists")
       else:
           urllib.request.urlretrieve(response_url,path[0] + model_name)


       return HttpResponseRedirect('/jobs/')



@myuser_login_required
@github_check
def list_jobs(request):
       jobs = Jobs.objects.order_by('-date')[:30]
       for job in jobs:
           import re
           list = re.findall("'(.*?)'", job.tubs)
           job.tubs = list


           if job.size != 'N/A':
              job.size=sizify(int(job.size))
       context = {
         'models': jobs,

       }
       template = loader.get_template('console/jobs.html')
       return HttpResponse(template.render(context, request))

def sizify(value):

    # value = ing(value)
    if value < 512000:
        value = value / 1024.0
        ext = 'kb'
    elif value < 4194304000:
        value = value / 1048576.0
        ext = 'mb'
    else:
        value = value / 1073741824.0
        ext = 'gb'
    return '%s %s' % (str(round(value, 2)), ext)

@myuser_login_required
@github_check
def list_jobs_success(request):
       jobs = Jobs.objects.order_by('-date')[:30]
       for job in jobs:
           import re
           list = re.findall("'(.*?)'", job.tubs)
           job.tubs = list
           if job.size != 'N/A':
              job.size=sizify(int(job.size))
       context = {
         'models': jobs,
        'success': "New Job Added !"

       }
       template = loader.get_template('console/jobs.html')
       return HttpResponse(template.render(context, request))


@myuser_login_required
@github_check
def list_jobs_timeout(request):
       jobs = Jobs.objects.order_by('-date')[:30]
       for job in jobs:
           import re
           list = re.findall("'(.*?)'", job.tubs)
           job.tubs = list
           if job.size != 'N/A':
              job.size=sizify(int(job.size))
       context = {
         'models': jobs,
        'timeout': "No Job was created ! Please Try again"

       }
       template = loader.get_template('console/jobs.html')
       return HttpResponse(template.render(context, request))

@myuser_login_required
@github_check
def list_jobs_fail(request):
       jobs = Jobs.objects.order_by('-date')[:30]
       for job in jobs:
           import re
           list = re.findall("'(.*?)'", job.tubs)
           job.tubs = list
           if job.size != 'N/A':
              job.size=sizify(int(job.size))
       context = {
         'models': jobs,
        'fail': " You don't have enough credits !"

       }
       template = loader.get_template('console/jobs.html')
       return HttpResponse(template.render(context, request))


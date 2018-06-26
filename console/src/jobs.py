
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
def delete_remark(request):
    id= request.GET.get('id', '')
    remarks.objects.filter(id=id).delete()
    return HttpResponseRedirect('/jobs/')


def delete_job(request):
    id= request.GET.get('id', '')
    Jobs.objects.filter(id=id).delete()
    return HttpResponseRedirect('/jobs/')
@myuser_login_required
@credentials_check
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
@myuser_login_required
@credentials_check
def verify_logs(state,id):

            conn = S3Connection(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            bucket = conn.get_bucket(AWS_ACCESS_KEY_ID.lower())
            s3 = boto3.resource('s3',aws_access_key_id=AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

            for key in bucket.list():

                if key.name == 'job_'+ str(id) +'.log':
                    #url = "https://s3.console.aws.amazon.com/s3/object/"+AWS_ACCESS_KEY_ID.lower()+"/"+ key.name
                    url_to_download= "https://s3.amazonaws.com/"+AWS_ACCESS_KEY_ID.lower()+"/"+ key.name
                    Jobs.objects.filter(id=id).update(log_url=url_to_download)
                    object_acl = s3.ObjectAcl(AWS_ACCESS_KEY_ID.lower(), key.name)
                    response = object_acl.put(ACL='public-read')


                if key.name == 'job_'+ str(id) +'_commands.log':
                    #url1 = "https://s3.console.aws.amazon.com/s3/object/"+AWS_ACCESS_KEY_ID.lower()+"/"+ key.name
                    url1_to_download= "https://s3.amazonaws.com/"+AWS_ACCESS_KEY_ID.lower()+"/"+ key.name
                    Jobs.objects.filter(id=id).update(commands_log_url=url1_to_download)
                    object_acl = s3.ObjectAcl(AWS_ACCESS_KEY_ID.lower(), key.name)
                    response1 = object_acl.put(ACL='public-read')
@myuser_login_required
@credentials_check
def cancel_request(request):
       client = boto3.client('ec2', aws_access_key_id=AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name='us-east-1')
       id = request.GET.get('id', '')
       job = Jobs.objects.get(id=id)
       client.terminate_instances(
           InstanceIds=[
               job.instance_id
           ]
       )
       Jobs.objects.filter(id=id).update(state='Canceled')
       Jobs.objects.filter(id=id).update(duration='0')
       return HttpResponseRedirect('/jobs/')

@myuser_login_required
@credentials_check
def update_status_by_id(request):
        client = boto3.client('ec2', aws_access_key_id=AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name='us-east-1')
        now = datetime.now(pytz.utc)
        id = request.GET.get('id', '')
        job = Jobs.objects.get(id=id)
        verify_logs(job.state,job.id)
        if job.request_id != "0":
                if now > job.date + timedelta(minutes=job.request_time):
                    try:
                        response = client.describe_spot_instance_requests(
                            SpotInstanceRequestIds=[
                                job.request_id
                            ]

                        )
                        value = response['SpotInstanceRequests'][0]['Status']['Code']
                        Jobs.objects.filter(id=job.id).update(request_state=value)
                        instance_id = response['SpotInstanceRequests'][0]['InstanceId']
                        Jobs.objects.filter(id=job.id).update(instance_id=instance_id)
                    except Exception as e:
                        print(e)


        now = datetime.now(pytz.utc)
        print("now",now)
        if job.state == 'Pending':
            if job.request_state == 'schedule-expired':
                Jobs.objects.filter(id=job.id).update(state='Failed')
                Jobs.objects.filter(id=job.id).update(duration='0')
            else:
                conn = S3Connection(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
                bucket = conn.get_bucket(AWS_ACCESS_KEY_ID.lower())
                for key in bucket.list('models'):
                    name = key.name.split('/')
                    print(key)
                    date = key.last_modified
                    print(date)
                    print("job.date" + str(job.date))
                    try:
                        updated_repo = github.objects.latest('id')
                        extension= updated_repo.extension
                    except:
                        extension = ''

                    if extension != '' :
                       model_name = 'job_' + str(job.id)+ extension
                    else:
                       model_name = 'job_' + str(job.id)

                    if name[1] == model_name:
                        Jobs.objects.filter(id=job.id).update(state='Finished')
                        Jobs.objects.filter(id=job.id).update(size=key.size)
                        duration = parse_datetime(date) - job.date
                        hours, minutes, seconds = convert_timedelta(duration)
                        time = str(minutes) + " m and " + str(seconds) + " s"
                        print(time)
                        Jobs.objects.filter(id=job.id).update(duration=time)
                    elif now > job.date + timedelta(minutes=job.instance_max):
                        Jobs.objects.filter(id=job.id).update(state='Failed')
                        Jobs.objects.filter(id=job.id).update(duration='0')


        return HttpResponseRedirect('/jobs/')



def convert_timedelta(duration):
    days, seconds = duration.days, duration.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    return hours, minutes, seconds
@myuser_login_required
@credentials_check
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
       if( os.path.exists(path[0]+model_name) == True ):
         print("it exists")
       else:
           s3.Object(AWS_ACCESS_KEY_ID.lower(),key_path.split('/', 1)[1] + '/' + model_name).download_file(path[0] + model_name)

       return HttpResponseRedirect('/jobs/')



@myuser_login_required
@credentials_check
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
@credentials_check
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



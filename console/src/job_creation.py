
import simplejson as json
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect

import json
import requests
from urllib.parse import urlparse
import os.path

import boto3
import base64
from operator import itemgetter
import os
from django.http import HttpResponse

from boto.s3.connection import S3Connection
from console.models import *
from console.views import myuser_login_required





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
def create_job(request):
        try:
            Local_directory = local_directory.objects.latest('id')
            updated_local_directory_name = Local_directory.name
        except:
            updated_local_directory_name = ''
        choices = ['t2.micro', 't2.medium', 'g2.2xlarge', 'g2.8xlarge', 'p2.xlarge', 'p3.2xlarge', 'p3.8xlarge']
        errorMessage = ""
        message = ""
        job_number = Jobs.objects.filter().count()
        if request.method == "POST":
            checked_data = request.POST.getlist('chk[]')
            instance_type = request.POST.get('choice')
            availability_zone = request.POST.get('AZ')
            max_time = request.POST.get('max_time')
            request_time = request.POST.get('request_time')
            facebook_id =request.session['userid']

            print(availability_zone)
            print(instance_type)
            print(max_time)
            print(request_time)

            if max_time == '':
                max_time = 15
            if request_time == '':
                request_time = 2
            try:
               availability_zone = availability_zone.split()
               price = availability_zone[1]
            except:
                print("no avai")

            print(checked_data)
            if len(checked_data) == 0 or int(max_time) >= 60:
                if len(checked_data) == 0 and int(max_time) >= 60:
                    message = " No selected items and EC2 Termination Time maximum must be 60 minutes "
                elif len(checked_data) == 0:
                    message = " No selected items"
                elif int(max_time) >= 60:
                    message = "EC2 Termination Time maximum must be 60 minutes "


            else:
                job = Jobs(
                    tubs=checked_data,
                    state="Pending",
                    job_number=job_number + 1,
                    instance=instance_type,
                    price=price,
                    availability_zone=availability_zone[0],
                    instance_max=max_time)
                job.save()
                selected_data = ""
                dataPath = os.popen('echo ~/'+updated_local_directory_name+'/data/').read()
                dataPath = dataPath.split()

                for dir in checked_data:
                    selected_data += " " + dir
                    print(selected_data)
                if len(selected_data) != 0:

                    try:
                        updated_repo = github.objects.latest('id')
                        extension= updated_repo.extension
                    except:
                        extension = ''
                    if extension != '' :
                       model_name = facebook_id+'_job_' + str(job.id)+ extension
                    else:
                       model_name = facebook_id+'_job_' + str(job.id)

                    job_name = facebook_id+'_job_' + str(job.id)

                    os.chdir(dataPath[0])
                    current_path = os.popen('pwd').read()
                    print(current_path)
                    os.system('tar -zcf   '+facebook_id+'_job_' + str(job.id) + '.tar.gz ' + selected_data)
                    tarfile_size = os.popen("ls -sh "+facebook_id+"_job_" + str(job.id) + ".tar.gz  | awk '{print $1}'").read()
                    print(tarfile_size)
                    Jobs.objects.filter(id=job.id).update(tarfile_size=tarfile_size)

                    current_path = os.popen('pwd').read()
                    current_path = current_path.split()
                    tarfile_name = job_name+'.tar.gz'

                    s3_data = {"name": tarfile_name}

                    url = "https://esx3owu58f.execute-api.us-east-1.amazonaws.com/dev/upload/to/S3"
                    headers = {'Content-type': 'application/json'}
                    response = requests.post(url, data=json.dumps(s3_data), headers=headers)
                    current_path = os.popen('pwd').read()
                    current_path = current_path.split()
                    print(current_path)
                    print(response.json())
                    response_url = (response.json())['url']

                    with open(current_path[0] + "/" + tarfile_name, 'rb') as data:
                        requests.put(response_url, data=data)

                    if instance_type != '':
                        termination_time = (Jobs.objects.get(id=job.id)).instance_max
                        github_repo = github.objects.latest('id')

                        data = { 'facebook_ID' : request.session['userid'],
                                'github_repo': github_repo.name, 'termination_time': termination_time,
                                'model_name': model_name, 'availability_zone': availability_zone[0], 'job_name':job_name,
                                'instance_type': instance_type, 'request_time': request_time}
                        url = "https://esx3owu58f.execute-api.us-east-1.amazonaws.com/dev/launchEC2"
                        headers = {'Content-type': 'application/json'}
                        response = requests.post(url, data=json.dumps(data), headers=headers)
                        print(response.json())

                        try:
                            Jobs.objects.filter(id=job.id).update(request_id=(json.loads(response.json()['body'])['request_id']))
                        except:
                            job.delete()
                        Jobs.objects.filter(id=job.id).update(date=datetime.now())
                        if "InvalidParameterValue" in response:
                            errorMessage = "This type of instance is invalid"
                            Jobs.objects.filter(id=job.id).delete()
                        elif "UnauthorizedOperation" in response:
                            errorMessage = "Check your IAM Permissions"
                            Jobs.objects.filter(id=job.id).delete()
                    else:
                        errorMessage = " Enter an instance type "


                    try:
                        msg = response.json()['message']
                        if msg == "Endpoint request timed out":
                            print("faaail")
                        return HttpResponseRedirect('/jobs/timeout/')
                    except Exception as  e:
                        print(e)

                        if (json.loads(response.json()['body'])['message'] == "You don't have enough credits"):
                            Jobs.objects.filter(id=job.id).delete()
                            return HttpResponseRedirect('/jobs/fail/')


                        elif json.loads(response.json()['body'])['message'] == "Try after an hour":
                            Jobs.objects.filter(id=job.id).delete()

                        else:
                            return HttpResponseRedirect('/jobs/success/')




                    os.system('rm -r  ' + facebook_id + '_job_' + str(job.id) + '.tar.gz ')


        list_data = os.popen('ls ~/'+updated_local_directory_name+'/data/').read()
        directories = list_data.split()
        dataFolders = []
        print(directories)
        for dir in directories:

            direcPath = os.popen('echo ~/'+updated_local_directory_name+'/data/' + dir).read()
            direcPath = direcPath.split()

            if os.path.isdir(direcPath[0]):

                if os.path.exists(direcPath[0] + '/donkeycar-console.json') == True:
                    print('it exists')
                else:
                    with open(direcPath[0] + '/donkeycar-console.json', 'w') as outfile:
                        noImages = os.popen('ls -l ~/'+updated_local_directory_name+'/data/' + dir + ' | grep .jpg | wc -l').read()
                        noImages.strip()
                        print(noImages)
                        noImages = int(noImages)

                        year = os.popen('date +"%Y"').read()
                        time = os.popen("ls -ldc ~/"+updated_local_directory_name+"/data/" + dir + " | awk  '{print $8}'").read()
                        month = os.popen("ls -ldc ~/"+updated_local_directory_name+"/data/" + dir + " | awk  '{print $6}'").read()
                        day = os.popen("ls -ldc ~/"+updated_local_directory_name+"/data/" + dir + " | awk  '{print $7}'").read()
                        date = year + " " + month + " " + day + " " + time
                        d = datetime.strptime(date, '%Y\n %b\n %d\n %H:%M\n')
                        d = d.strftime('%Y-%m-%d %H:%M')
                        json.dump({"name": dir, "no": noImages, "date": d, "remarks": []}, outfile)

                with open(direcPath[0] + '/donkeycar-console.json', 'r') as result:
                    data = json.load(result)
                    dataFolders.append(data)

        dataFolders.sort(key=itemgetter('date'), reverse=True)
        jobs = Jobs.objects.order_by('-date')[:30]
        for job in jobs:
           if job.size != 'N/A':
              job.size = sizify(int(job.size))


        context = {
            'models': jobs,
            'result': dataFolders,
            'message': message,
            'errorMessage': errorMessage,
            'choices': choices,


        }
        return render(request, 'console/create_job.html',context)
#def check_availability_zone(instance_type):
  #  client = boto3.client('ec2', aws_access_key_id=AWS_ACCESS_KEY_ID,
                         # aws_secret_access_key=AWS_SECRET_ACCESS_KEY,region_name='us-east-1')
   # response = client.describe_spot_price_history(
   # InstanceTypes=[
    #    instance_type
   # ],
   # ProductDescriptions=[
     #   'Linux/UNIX',
    #],
      #  MaxResults=6,

    #)


    #List= response['SpotPriceHistory']
    #List.sort(key=itemgetter('SpotPrice'))

   # models = { az['AvailabilityZone'] for az in List}
    #listAZ = list(models)

    #newlist=[]
    #for l in listAZ:
     #   listA = [x for x in List if x['AvailabilityZone']== l]
      #  newlist.append(l + " " + listA[0]['SpotPrice']  + "/H")


 #   return newlist

@myuser_login_required
def display_availability(request,name):
       # response = check_availability_zone(name)
       data = {'instance_type': name}
       url = "https://esx3owu58f.execute-api.us-east-1.amazonaws.com/dev/availabilityzone"
       headers = {'Content-type': 'application/json'}
       response = requests.post(url, data=json.dumps(data), headers=headers)

       print("heyy",response.json())
       return HttpResponse(json.loads(response.json()['body'])['AZ'])
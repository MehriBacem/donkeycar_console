import simplejson as json
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
import json
import os.path
from operator import itemgetter
import os
import zipfile
from django.http import HttpResponse
import io
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
def display_data_folders(request):
        try:
            Local_directory = local_directory.objects.latest('id')
            updated_local_directory_name = Local_directory.name
        except:
            updated_local_directory_name = ''

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
        print(dataFolders)
        context = {
            'result': dataFolders,
        }

        return render(request, 'console/data_folders.html', context)
@myuser_login_required
@github_check
def getfiles(request):
        try:
            Local_directory = local_directory.objects.latest('id')
            updated_local_directory_name = Local_directory.name
        except:
            updated_local_directory_name = ''
        result = request.GET.get('dir', '')
        print(result)
        zip_io = io.BytesIO()
        direcPath = os.popen('echo ~/'+updated_local_directory_name+'/data/').read()
        direcPath = direcPath.split()
        with zipfile.ZipFile(zip_io, mode='w', compression=zipfile.ZIP_DEFLATED) as backup_zip:
            for f in os.listdir(direcPath[0] + result):
                backup_zip.write(direcPath[0] + result + '/' + f)

        response = HttpResponse(zip_io.getvalue(), content_type='application/x-zip-compressed')
        response['Content-Disposition'] = 'attachment; filename=%s' % result + ".zip"
        response['Content-Length'] = zip_io.tell()
        return response
@myuser_login_required
@github_check
def delete_data(request):
    name= request.GET.get('name', '')
    try:
        Local_directory = local_directory.objects.latest('id')
        updated_local_directory_name = Local_directory.name
    except:
        updated_local_directory_name = ''
    os.system('sudo rm -r ~/'+updated_local_directory_name+'/data/'+name)
    return HttpResponseRedirect('/data/')


@myuser_login_required
@github_check
def delete_empty_folders(request):
    try:
        Local_directory = local_directory.objects.latest('id')
        updated_local_directory_name = Local_directory.name
    except:
        updated_local_directory_name = ''

    list_data = os.popen('ls ~/' + updated_local_directory_name + '/data/').read()

    directories = list_data.split()
    print(directories)
    for dir in directories:

        direcPath = os.popen('echo ~/' + updated_local_directory_name + '/data/' + dir).read()
        direcPath = direcPath.split()

        if os.path.isdir(direcPath[0]):

                    noImages = os.popen(
                        'ls -l ~/' + updated_local_directory_name + '/data/' + dir + ' | grep .jpg | wc -l').read()
                    noImages.strip()
                    print(noImages)
                    noImages = int(noImages)

                    if noImages == 0 :
                        os.system('sudo rm -r '+direcPath[0])

    return HttpResponseRedirect('/data/')

@myuser_login_required
@github_check
def delete_data_folder_comment(request):

    comment= request.GET.get('comment', '')
    name= request.GET.get('name', '')
    try:
        Local_directory = local_directory.objects.latest('id')
        updated_local_directory_name = Local_directory.name
    except:
        updated_local_directory_name = ''

    if (id and name):
        direcPath = os.popen('echo ~/'+updated_local_directory_name+'/data/' + name).read()
        direcPath = direcPath.split()
        with open(direcPath[0] + '/donkeycar-console.json', 'r') as outfile:
            data = json.load(outfile)
        with open(direcPath[0] + '/donkeycar-console.json', 'w') as writefile:
            (data['remarks']).remove(comment)
            json.dump(data, writefile)

    return HttpResponseRedirect('/data/')
@myuser_login_required
@github_check
def add_data_folder_comment(request):


    data_name = request.POST['name']
    print(data_name)
    data_comment = request.POST['var']
    try:
        Local_directory = local_directory.objects.latest('id')
        updated_local_directory_name = Local_directory.name
    except:
        updated_local_directory_name = ''
    direcPath = os.popen('echo ~/'+updated_local_directory_name+'/data/' + data_name).read()
    direcPath = direcPath.split()
    with open(direcPath[0] + '/donkeycar-console.json', 'r') as outfile:
            data = json.load(outfile)
            print(data['remarks'])
            print(len(data['remarks']))
    with open(direcPath[0] + '/donkeycar-console.json', 'w') as writefile:
            (data['remarks']).append(data_comment)
            json.dump(data, writefile)
    return HttpResponse('success')

from django.template import loader
import os.path
import boto3
import os
from django.http import HttpResponse
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from console.models import *
from console.views import myuser_login_required

@myuser_login_required
def save_local_directory(request):
    message = ""
    updated_repo = ""
    try:
        credential = credentials.objects.latest('id')
        aws_key_id = credential.aws_access_key_id
    except:
        aws_key_id = ''
    if request.method == "POST":
        local_directory_name = request.POST.get('local_directory')

        if local_directory_name != None:

            try:
                exist_local_directory = local_directory.objects.latest('id')
                local_directory.objects.filter(id=exist_local_directory.id).update(name=local_directory_name)

                message = "Local Directory  has been updated"

            except:
                new_local_directory = local_directory(name=local_directory_name)
                new_local_directory.save()
                message = "Local Directory has been saved"
    try:
        updated_name = github.objects.latest('id')
        updated_repo_name = updated_name.name
        updated_extension = updated_name.extension
    except:
        updated_repo_name = ''
        updated_extension = ''
    try:
        updated_controller = controller.objects.latest('id')
        updated_training_controller = updated_controller.training
    except:
        updated_training_controller = ''
    try:
        updated_local_directory = local_directory.objects.latest('id')
        updated_local_directory_name = updated_local_directory.name
    except:
        updated_local_directory_name = ''

    template = loader.get_template('console/local_directory.html')
    return HttpResponse(template.render({'status': message, 'local_directory': updated_local_directory_name,
                                         'training_controller': updated_training_controller,
                                         'updated_extension': updated_extension, 'updated_repo': updated_repo_name,
                                         'AWS_KEY': aws_key_id}, request))
@myuser_login_required
def save_github_repo(request):
    message = ""
    updated_repo = ""
    try:
        credential = credentials.objects.latest('id')
        aws_key_id = credential.aws_access_key_id
    except:
        aws_key_id = ''
    if request.method == "POST":
        repo = request.POST.get('repo')
        extension = request.POST.get('extension')

        print(repo)

        result = os.system('git ls-remote  ' + repo)
        if result == 0:
            if repo != None:
                try:
                   exist_repo = github.objects.latest('id')
                   github.objects.filter(id=exist_repo.id).update(name=repo)
                   github.objects.filter(id=exist_repo.id).update(extension=extension)
                   message = "Github Repository has been updated"
                except:
                   new_github = github(name=repo,extension=extension)
                   new_github.save()
                   message = "Github Repository has been updated"


        else:
            message = "Please enter a git repository"
    try:
        updated_name = github.objects.latest('id')
        updated_repo_name = updated_name.name
        updated_extension = updated_name.extension
    except:
        updated_repo_name = ''
        updated_extension = ''
    try:
        updated_controller = controller.objects.latest('id')
        updated_training_controller = updated_controller.training
    except:
        updated_training_controller = ''

    try:
        updated_local_directory = local_directory.objects.latest('id')
        updated_local_directory_name = updated_local_directory.name
    except:
        updated_local_directory_name = ''


    template = loader.get_template('console/github.html')
    return HttpResponse(template.render({'status': message,'local_directory': updated_local_directory_name,'training_controller':updated_training_controller,'updated_extension':updated_extension,'updated_repo':updated_repo_name,'AWS_KEY':aws_key_id}, request))



@myuser_login_required
def save_controller_settings(request):
    message = ""
    updated_repo = ""
    try:
        credential = credentials.objects.latest('id')
        aws_key_id = credential.aws_access_key_id
    except:
        aws_key_id = ''
    if request.method == "POST":
        training_controller = request.POST.get('training_controller')

        if training_controller != None :
            try:
                exist_controller = controller.objects.latest('id')
                controller.objects.filter(id=exist_controller.id).update(training=training_controller)

                message = "Controller settings have been updated"
            except Exception as e:

                new_controller = controller(
                    training=training_controller)
                new_controller.save()
                message = "Controller settings have been updated"




    try:
        updated_name = github.objects.latest('id')
        updated_repo_name = updated_name.name
        updated_extension = updated_name.extension
    except:
        updated_repo_name = ''
        updated_extension = ''
    try:
        updated_controller = controller.objects.latest('id')
        updated_training_controller = updated_controller.training
    except:
        updated_training_controller = ''

    try:
        updated_local_directory = local_directory.objects.latest('id')
        updated_local_directory_name = updated_local_directory.name
    except:
        updated_local_directory_name = ''

    template = loader.get_template('console/controller.html')
    return HttpResponse(template.render({'local_directory': updated_local_directory_name,'controller_message': message,'training_controller':updated_training_controller,'updated_extension':updated_extension,'updated_repo':updated_repo_name,'AWS_KEY':aws_key_id}, request))



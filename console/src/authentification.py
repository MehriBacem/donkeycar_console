from django.template import loader
from django.http import HttpResponse
from console.models import *
import requests
import json

from django.http import HttpResponse,HttpResponseRedirect

def login(request,accessToken):
    data = {'accessToken': accessToken}
    url = "https://38qhfwpc5j.execute-api.us-east-1.amazonaws.com/dev/user/login"
    headers = {'Content-type': 'application/json'}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    try:
        body = json.loads(response.json()['body'])
        jwt_token = body['Token']
        user_id = body['UserID']
        name = body['name']
        profile_image = body['profileImage']


        count = facebook_user.objects.filter(facebook_id=user_id).count()
        print(count)
        if count == 0 :

            new_user = facebook_user(JWT_token=jwt_token,facebook_id=user_id,name=name,profile_picture_url=profile_image)
            new_user.save()
        else:
            facebook_user.objects.filter(facebook_id=user_id).update(JWT_token=jwt_token)

        request.session['userid'] = user_id
        request.session['name'] = name
        request.session['profile_picture'] = profile_image

        return HttpResponse('True')
    except Exception as e :
        return  HttpResponse('False')




def logout(request):
        try:
            del request.session['userid']
        except:
            pass
        return HttpResponseRedirect('/')


def get_user_info(request):

    if 'userid' in request.session:

        name = request.session['name']
        profile_picture_url = request.session['profile_picture']

        response =  name+"&&"+profile_picture_url

    else:
        response=""

    return HttpResponse(response)






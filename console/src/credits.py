import json
import requests

from console.models import *
from django.http import HttpResponse,HttpResponseRedirect

import urllib

def enquire_credits(request):

    if 'userid' in request.session:

        try:
            user = facebook_user.objects.get(facebook_id=request.session['userid'])
            print(user.JWT_token)
        except facebook_user.DoesNotExist:
            print("doesn't exist")
            user = None
        data = {'UserID': request.session['userid']}
        url1 = 'https://esx3owu58f.execute-api.us-east-1.amazonaws.com/dev/credits/enquire'
        headers1 = {'Authorization': user.JWT_token}

        response1 = requests.post(url1,data=json.dumps(data), headers=headers1)

    try:
        num = response1.json()['number']
        return HttpResponse(num)
    except:
        return HttpResponse("Unauthorized")


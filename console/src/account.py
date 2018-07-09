from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.template import loader
from django.http import HttpResponse

import stripe
import requests
import json

def one():
    return "7"


def two():
    return "14"


def three():
    return "20"

def five():
    return "30"

def seven():
    return "40"

def ten():
    return "50"

switcher = {
    "1": one,
    "2": two,
    "3": three,
    "5": five,
    "7": seven,
    "10": ten
}


def numbers_to_strings(argument):
    func = switcher.get(argument, "nothing")
    return func()


def account(request):
    data = {'UserID':request.session['userid']}
    url1 = 'https://j9p3fxvn66.execute-api.us-east-1.amazonaws.com/dev/transactions/list'
    response1 = requests.post(url1, data=json.dumps(data))
    print(response1.json())
    context = {
        'list': json.loads(response1.json()['body']),
    }

    template = loader.get_template('console/account.html')
    return HttpResponse(template.render(context, request))


def new_topup(request):
    choices = [ [0,'2',2,200], [1,'3',3,300], [2,'5',4,400], [3,'7',5,500], [4,'10',8,800]]
    context = {
        'key': 'pk_test_NzJne5coqRIodACfwoKaSqGd',
        'choices': choices,
    }
    template = loader.get_template('console/topup.html')
    return HttpResponse(template.render(context, request))


def display_payment(request,credits):


    number = numbers_to_strings(credits)
    print(number)

    return HttpResponse(number)

def get_payment_infos(request,name):

    return HttpResponse(name)


def charge(request):

        val = request.POST.get('hidden')
        credits =  request.POST.get('credits_number')
        print("cents",val)
        print("credits",credits)
        token = request.POST.get('stripeToken', '')
        data = {'token': token,'credits':credits,'cents': val,'UserID':request.session['userid']}
        url1 = 'https://j9p3fxvn66.execute-api.us-east-1.amazonaws.com/dev/topup'
        response1 = requests.post(url1,data=json.dumps(data))
        print(response1.json())

        return HttpResponseRedirect('/account/')

















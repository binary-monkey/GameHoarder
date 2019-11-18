import csv
import json

from django.contrib.auth import authenticate, login
from django.template.context_processors import csrf
from django.contrib import auth
from .forms import *
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from game_collection.models import Tag

def index(request):
    custom = Tag.objects.filter(user=request.user)

    context = {
        "tags": custom
    }
    return render(request, "index.html", context)

def friends(request):
    return render(request, "index.html")

def download_csv(request):
    if request.method == 'POST':
        response = HttpResponse(content_type='text/csv')
        data = request.POST.getlist("data")

        response['Content-Disposition'] = 'attachment; filename="%s.csv"' % request.POST.get("filename")

        writer = csv.writer(response)

        headers = json.loads(data[0].replace("'", '"'))
        writer.writerow(headers.keys())

        for row in data:
            title = json.loads(row.replace("'", '"'))

            if 'original_title' in title:
                title["game"] = title["original_title"]
                title.pop("original_title")

            writer.writerow(list(title.values()))

        return response


def login_register(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('login')
        else:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect('/es/')
    else:
        form = UserForm


    token = {}
    token.update(csrf(request))
    token['form'] = form

    return render(request, 'login_register.html')

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("login")
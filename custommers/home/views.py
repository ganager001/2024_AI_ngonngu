from django.shortcuts import render
import json
import os
from django.conf import settings
from django.http import JsonResponse
from django.http import HttpResponse
from common import *
from django.contrib.auth.decorators import login_required

@login_required()
def home(request):
    # data = read_json_file()
    # data = {"posts": read_json_file()}
    return render(request, "custommer/home/index.html", context = {})

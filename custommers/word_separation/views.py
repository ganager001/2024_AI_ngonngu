from django.shortcuts import render
import json
import os
from django.conf import settings
from django.http import JsonResponse
from django.http import HttpResponse
from common import *
from django.contrib.auth.decorators import login_required



def read_json_file():
    file_path = os.path.join(settings.BASE_DIR, 'common\\data-final.json')
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


@login_required()
def index(request):
    # data = read_json_file()
    data = {"posts": read_json_file()}
    return render(request, "custommer/word_separation/index.html", context = data)
    # data = read_json_file()
    # return JsonResponse(data, safe=False)

@login_required()
def detail(request, id):
    file_path = os.path.join(settings.BASE_DIR, 'common\\data-final.json')
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        article = next((item for item in data if item["id"] == id), None)
        if article:
            return JsonResponse(article, safe=False)
        else:
            return JsonResponse({"error": "Article not found"}, status=404)
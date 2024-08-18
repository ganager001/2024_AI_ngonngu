from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
import json, os
from cores.xl_phan_cum import perform_clustering
from django.http import HttpResponse
from datetime import datetime
import math



@login_required()
def index(request):
    data = {}
    return render(request, "custommer/clustering_app/cluster_result.html", context = data)



def load_data(start_date,end_date):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(current_dir, '..', 'common', 'data_gan_nhan.json')
    data_file = os.path.abspath(data_file)
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    filtered_data = []

    if start_date:
        start_date = datetime.strptime(start_date, '%m/%d/%Y')
    if end_date:
        end_date = datetime.strptime(end_date, '%m/%d/%Y')

    for item in data:
        item_date_str = item.get('time')  # Giả sử có trường 'date'
        if item_date_str:
            try:
                item_date = datetime.strptime(item_date_str, '%d/%m/%Y')
                if start_date and end_date:
                    if start_date <= item_date <= end_date:
                        filtered_data.append(item)
            except:
                pass
                continue
 
    return filtered_data
    

@login_required()
def cluster_view(request):
    return render(request, 'custommer/clustering_app/cluster_result.html')


@login_required()
def data_filter(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'GET':
        start_date = request.GET['start-date']
        end_date = request.GET['end-date']
        data = load_data(start_date,end_date)
        items = perform_clustering(data)
        for item in items['cluster_results']:
            item['titles'] = item['titles'].split('\n')

        paginations = {}
        if(items['results']):
            paginations['total_pages'] = int(math.ceil(len(items['results']) / 10))
            paginations['page'] = 1
            paginations['count'] = 0
        else:
            total_pages = 0
        return render(request, 'custommer/clustering_app/data_find.html', {'items': items, 'paginations':paginations})
    return HttpResponse(status=400)









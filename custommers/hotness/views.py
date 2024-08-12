from django.shortcuts import render
from cores.xl_do_nong import calculate_hotness
import os

def hotness_view(request):
    current_dir = os.path.dirname(os.path.abspath(__file__))    
    input_file = os.path.join(current_dir, '../..', 'common', 'data_gan_nhan.json')  # Cập nhật đường dẫn thực tế
    results = calculate_hotness(input_file)
    
    hotness_data = results.to_dict('records')
    
    context = {
        'hotness_data': hotness_data
    }
    return render(request, 'custommer/hotness/index.html', context)
import os
import json
import matplotlib.pyplot as plt
import io
import base64
from django.shortcuts import render
from cores.xl_do_nong import calculate_hotness

def prepare_hotness_data(input_file):
    results = calculate_hotness(input_file)
    hotness_data = results.to_dict('records')
    
    chart_data = []
    for row in hotness_data:
        radius = row['H'] * 20  # Tính toán bán kính
        chart_data.append({
            'topic': f"Chủ đề {row['Cum_chu_de']}",
            'hotness': row['H'],
            'total_posts': row['So_bai_viet'],
            'total_likes': row['Tong_likes'],
            'total_comments': row['Tong_comments'],
            'keywords': row['Keywords'],
            'radius': radius,
            'diameter': radius * 2  # Tính toán đường kính
        })
    
    return hotness_data, chart_data

def generate_circle_images(chart_data):
    images = []
    for item in chart_data:
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.add_patch(plt.Circle((0.5, 0.5), item['radius']/100, color='lightblue', ec='black'))
        ax.text(0.5, 0.5, f"{item['total_posts']}", horizontalalignment='center', verticalalignment='center', fontsize=12)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect('equal', 'box')
        ax.axis('off')
        
        # Lưu hình ảnh vào bộ nhớ
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        
        images.append({
            'topic': item['topic'],
            'total_likes': item['total_likes'],
            'total_comments': item['total_comments'],
            'keywords': item['keywords'],
            'image': image_base64
        })
        plt.close(fig)
    return images

def hotness_view(request):
    current_dir = os.path.dirname(os.path.abspath(__file__))    
    input_file = os.path.join(current_dir, '../..', 'common', 'data_gan_nhan.json')
    hotness_data, chart_data = prepare_hotness_data(input_file)
    
    # Tạo hình ảnh cho các hình tròn
    circle_images = generate_circle_images(chart_data)

    context = {
        'hotness_data': hotness_data,
        'circle_images': circle_images
    }
    return render(request, 'custommer/hotness/index.html', context)
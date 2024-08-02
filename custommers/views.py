from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import JsonResponse
import psutil

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('custommer')  # Hoặc bất kỳ URL nào bạn muốn chuyển hướng tới
        else:
            # Xử lý lỗi đăng nhập
            pass
    return render(request, 'custommer/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def system_info(request):
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    data = {
        'cpu_percent': float(cpu_percent),
        'memory_used': float(memory.percent),
        'disk_used': float(disk.percent),
    }
    return JsonResponse(data)


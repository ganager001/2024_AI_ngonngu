from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('custommers')  # Hoặc bất kỳ URL nào bạn muốn chuyển hướng tới
        else:
            # Xử lý lỗi đăng nhập
            pass
    return render(request, 'custommer/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')


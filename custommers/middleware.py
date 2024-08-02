from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Danh sách các URL không yêu cầu đăng nhập (ví dụ: trang đăng nhập, đăng ký, và các trang tĩnh)
        # exempt_urls = [reverse('login'), reverse('signup')]  # Thêm các URL bạn muốn bỏ qua
        exempt_urls = [reverse('login'), reverse('logout')]
        if request.path not in exempt_urls and not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)
        response = self.get_response(request)
        return response

# apps.py
from django.apps import AppConfig

class CustommerConfig(AppConfig):
    name = 'custommers'  # Thay đổi 'common' thành tên ứng dụng của bạn

    def ready(self):
        from . import signals  # Thay đổi 'common' thành tên ứng dụng của bạn

from django.urls import path, include
from .views import *
urlpatterns = [
    path('', index, name='sticker'),
    path('<int:id>/', detail, name='get_sticker_by_id'),
]
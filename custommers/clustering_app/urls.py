from django.urls import path
from .views import *

urlpatterns = [
    path('', cluster_view, name='clustering'),
    path('data_filter/', data_filter, name='data_filter'),
]

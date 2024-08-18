from django.urls import path
from . import views

urlpatterns = [
    path('', views.hotness_view, name='hotness'),
    path('hotness_filter/', views.hotness_filter, name='hotness_filter'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.hotness_view, name='hotness'),
]
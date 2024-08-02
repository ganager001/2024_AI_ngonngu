from django.urls import path, include
from .views import *
urlpatterns = [
    path('', index, name='custommers_post'),
    path('<int:id>/', detail, name='get_article_by_id'),
]
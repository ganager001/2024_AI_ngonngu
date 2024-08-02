from django.urls import path, include
from .views import *
urlpatterns = [
    path('', index, name='wordseparation'),
    path('<int:id>/', detail, name='get_wordseparation_by_id'),
]
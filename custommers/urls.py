from django.urls import path, include
from .views import *

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', include("custommers.home.urls")),
    path('post/', include("custommers.post.urls")), # bài viết 
    path('wordseparation/', include("custommers.word_separation.urls")), # tách từ 
    path('sticker/', include("custommers.sticker.urls")), # gán nhãn
]
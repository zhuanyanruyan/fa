from django.urls import path
from . import views

urlpatterns = [
    path('update_comment', views.update_comment, name='update_comment')
]
# 写成了 {} 调了一个小时

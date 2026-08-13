from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.thread_list, name='list'),
    path('<int:pk>/', views.thread_detail, name='detail'),
    path('create/', views.thread_create, name='create'),
    path('<int:pk>/reply/', views.add_reply, name='reply'),
    path('reply/<int:pk>/upvote/', views.upvote_reply, name='upvote'),
    path('<int:pk>/lock/', views.toggle_lock, name='lock'),
]
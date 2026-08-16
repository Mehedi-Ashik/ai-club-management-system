from django.urls import path
from . import views
from . import api_views

app_name = 'events'

urlpatterns = [
    path('', views.event_list, name='list'),
    path('create/', views.event_create, name='create'),
    path('<int:pk>/', views.event_detail, name='detail'),
    path('<int:pk>/register/', views.event_register, name='register'),
    path('api/', api_views.event_list_api, name='api_list'),
    path('api/<int:pk>/', api_views.event_detail_api, name='api_detail'),
]
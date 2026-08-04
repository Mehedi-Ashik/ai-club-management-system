from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    path('', views.member_list, name='list'),
    path('apply/', views.apply_membership, name='apply'),
    path('applications/', views.application_list, name='applications'),
    path('approve/<int:pk>/', views.approve_application, name='approve'),
    path('reject/<int:pk>/', views.reject_application, name='reject'),
]
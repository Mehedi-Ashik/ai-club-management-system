from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('mark/<int:event_id>/', views.mark_attendance, name='mark'),
    path('report/<int:event_id>/', views.attendance_report, name='report'),
]
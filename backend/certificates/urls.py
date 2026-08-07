from django.urls import path
from . import views

app_name = 'certificates'

urlpatterns = [
    path('generate/<int:event_id>/', views.generate_certificates, name='generate'),
    path('my/', views.my_certificates, name='my_certificates'),
    path('download/<int:cert_id>/', views.download_certificate, name='download'),
    path('verify/<uuid:certificate_id>/', views.verify_certificate, name='verify'),
]
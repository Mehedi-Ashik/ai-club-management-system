from django.contrib import admin
from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('member', 'event', 'certificate_id', 'issued_at')
    list_filter = ('event',)
    search_fields = ('member__username', 'event__title')
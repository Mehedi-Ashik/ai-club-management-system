from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'amount', 'status', 'tran_id', 'created_at']
    list_filter = ['status']
    search_fields = ['tran_id', 'user__username', 'event__title']
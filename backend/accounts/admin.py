from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Member


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Role', {'fields': ('role', 'is_verified')}),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Member)
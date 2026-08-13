from django.contrib import admin
from .models import ForumThread, ForumReply


@admin.register(ForumThread)
class ForumThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_locked', 'created_at')
    list_filter = ('is_locked',)
    search_fields = ('title', 'content')


@admin.register(ForumReply)
class ForumReplyAdmin(admin.ModelAdmin):
    list_display = ('thread', 'author', 'created_at')
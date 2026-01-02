from django.contrib import admin
from .models import ChatSession, ChatMessage


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ['role', 'content', 'created_at']
    can_delete = False


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'updated_at', 'message_count']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['session_key', 'created_at', 'updated_at']
    inlines = [ChatMessageInline]

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Сообщений'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'role', 'short_content', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['content']
    readonly_fields = ['session', 'role', 'content', 'created_at']

    def short_content(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    short_content.short_description = 'Содержание'

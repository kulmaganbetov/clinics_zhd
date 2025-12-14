from django.contrib import admin
from .models import ClinicInfo, SliderImage, Service, News, ContactMessage


@admin.register(ClinicInfo)
class ClinicInfoAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'phone', 'email']


@admin.register(SliderImage)
class SliderImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_published', 'published_at', 'created_at']
    list_filter = ['is_published']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['name', 'email', 'phone', 'subject', 'message', 'created_at']
    date_hierarchy = 'created_at'

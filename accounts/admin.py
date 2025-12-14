from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, DoctorProfile, NurseProfile


class DoctorProfileInline(admin.StackedInline):
    model = DoctorProfile
    can_delete = False
    verbose_name = 'Профиль врача'


class NurseProfileInline(admin.StackedInline):
    model = NurseProfile
    can_delete = False
    verbose_name = 'Профиль медсестры'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'get_full_name', 'role', 'phone', 'is_active']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['username', 'first_name', 'last_name', 'patronymic', 'iin', 'phone']
    ordering = ['last_name', 'first_name']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('role', 'patronymic', 'phone', 'iin', 'birth_date', 'avatar')}),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Дополнительно', {'fields': ('role', 'first_name', 'last_name', 'patronymic', 'phone')}),
    )

    def get_inline_instances(self, request, obj=None):
        if obj:
            if obj.role == User.Role.DOCTOR:
                return [DoctorProfileInline(self.model, self.admin_site)]
            elif obj.role == User.Role.NURSE:
                return [NurseProfileInline(self.model, self.admin_site)]
        return []


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'cabinet', 'experience_years', 'category']
    list_filter = ['specialization', 'category']
    search_fields = ['user__last_name', 'user__first_name', 'specialization']


@admin.register(NurseProfile)
class NurseProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'qualification']
    list_filter = ['department']
    search_fields = ['user__last_name', 'user__first_name', 'department']

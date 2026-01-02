from django.contrib import admin
from .models import Patient, Schedule, Appointment


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'iin', 'birth_date', 'gender', 'phone', 'is_attached']
    list_filter = ['gender', 'is_attached', 'attachment_date']
    search_fields = ['last_name', 'first_name', 'patronymic', 'iin', 'phone']
    date_hierarchy = 'attachment_date'

    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'iin', 'last_name', 'first_name', 'patronymic', 'birth_date', 'gender')
        }),
        ('Контакты', {
            'fields': ('phone', 'email', 'address', 'registration_address', 'workplace')
        }),
        ('Медицинская информация', {
            'fields': ('blood_type', 'allergies', 'chronic_diseases')
        }),
        ('Прикрепление', {
            'fields': ('is_attached',)
        }),
    )
    readonly_fields = ['attachment_date']




@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'day_of_week', 'start_time', 'end_time', 'slot_duration', 'is_active']
    list_filter = ['day_of_week', 'is_active', 'doctor']
    list_editable = ['is_active']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'doctor', 'date', 'time', 'appointment_type', 'status']
    list_filter = ['status', 'appointment_type', 'date', 'doctor']
    search_fields = ['patient__last_name', 'patient__first_name', 'patient__iin']
    date_hierarchy = 'date'
    raw_id_fields = ['patient', 'doctor', 'created_by']

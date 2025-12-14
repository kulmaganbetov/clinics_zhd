from django.urls import path
from . import views

app_name = 'registry'

urlpatterns = [
    # Пациенты
    path('patients/', views.PatientListView.as_view(), name='patient_list'),
    path('patients/create/', views.PatientCreateView.as_view(), name='patient_create'),
    path('patients/<int:pk>/', views.PatientDetailView.as_view(), name='patient_detail'),

    # Расписание
    path('schedule/', views.ScheduleListView.as_view(), name='schedule_list'),

    # Записи на приём
    path('appointments/', views.AppointmentListView.as_view(), name='appointment_list'),
    path('appointments/create/', views.AppointmentCreateView.as_view(), name='appointment_create'),
    path('appointments/<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment_detail'),
    path('appointments/<int:pk>/edit/', views.AppointmentUpdateView.as_view(), name='appointment_edit'),

    # Мои записи (для пациентов)
    path('my-appointments/', views.MyAppointmentsView.as_view(), name='my_appointments'),
]

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from datetime import date, timedelta
from .models import Patient, Schedule, Appointment
from accounts.models import User


class PatientListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Список пациентов"""
    model = Patient
    template_name = 'registry/patient_list.html'
    context_object_name = 'patients'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_doctor or self.request.user.is_nurse

    def get_queryset(self):
        queryset = Patient.objects.all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(last_name__icontains=search) |
                Q(first_name__icontains=search) |
                Q(iin__icontains=search) |
                Q(phone__icontains=search)
            )
        return queryset


class PatientDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Карточка пациента"""
    model = Patient
    template_name = 'registry/patient_detail.html'
    context_object_name = 'patient'

    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_doctor or self.request.user.is_nurse


class PatientCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Создание пациента"""
    model = Patient
    template_name = 'registry/patient_form.html'
    fields = ['iin', 'last_name', 'first_name', 'patronymic', 'birth_date', 'gender',
              'phone', 'email', 'address', 'registration_address', 'workplace',
              'blood_type', 'allergies', 'chronic_diseases']
    success_url = reverse_lazy('registry:patient_list')

    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_nurse

    def form_valid(self, form):
        messages.success(self.request, 'Пациент успешно зарегистрирован')
        return super().form_valid(form)


class ScheduleListView(LoginRequiredMixin, ListView):
    """Расписание врачей"""
    model = Schedule
    template_name = 'registry/schedule_list.html'
    context_object_name = 'schedules'

    def get_queryset(self):
        queryset = Schedule.objects.filter(is_active=True).select_related('doctor', 'doctor__doctor_profile')
        doctor_id = self.request.GET.get('doctor')
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        return queryset.order_by('day_of_week', 'start_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['doctors'] = User.objects.filter(role=User.Role.DOCTOR)
        return context


class AppointmentListView(LoginRequiredMixin, ListView):
    """Список записей на приём"""
    model = Appointment
    template_name = 'registry/appointment_list.html'
    context_object_name = 'appointments'
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        queryset = Appointment.objects.select_related('patient', 'doctor')

        # Фильтрация по роли
        if user.is_doctor:
            queryset = queryset.filter(doctor=user)
        elif user.is_patient:
            try:
                patient = Patient.objects.get(user=user)
                queryset = queryset.filter(patient=patient)
            except Patient.DoesNotExist:
                queryset = Appointment.objects.none()

        # Фильтры
        date_filter = self.request.GET.get('date')
        status_filter = self.request.GET.get('status')

        if date_filter:
            queryset = queryset.filter(date=date_filter)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by('-date', '-time')


class AppointmentCreateView(LoginRequiredMixin, CreateView):
    """Создание записи на приём"""
    model = Appointment
    template_name = 'registry/appointment_form.html'
    fields = ['patient', 'doctor', 'date', 'time', 'appointment_type', 'reason']
    success_url = reverse_lazy('registry:appointment_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['doctors'] = User.objects.filter(role=User.Role.DOCTOR).select_related('doctor_profile')
        context['patients'] = Patient.objects.all()[:100]
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Запись успешно создана')
        return super().form_valid(form)


class AppointmentDetailView(LoginRequiredMixin, DetailView):
    """Детали записи"""
    model = Appointment
    template_name = 'registry/appointment_detail.html'
    context_object_name = 'appointment'


class AppointmentUpdateView(LoginRequiredMixin, UpdateView):
    """Обновление записи"""
    model = Appointment
    template_name = 'registry/appointment_form.html'
    fields = ['status', 'notes']
    success_url = reverse_lazy('registry:appointment_list')

    def form_valid(self, form):
        messages.success(self.request, 'Запись обновлена')
        return super().form_valid(form)


class MyAppointmentsView(LoginRequiredMixin, ListView):
    """Мои записи (для пациентов)"""
    model = Appointment
    template_name = 'registry/my_appointments.html'
    context_object_name = 'appointments'

    def get_queryset(self):
        user = self.request.user
        try:
            patient = Patient.objects.get(user=user)
            return Appointment.objects.filter(patient=patient).select_related('doctor').order_by('-date', '-time')
        except Patient.DoesNotExist:
            return Appointment.objects.none()

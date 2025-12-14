from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import ClinicInfo, SliderImage, Service, News, ContactMessage
from accounts.models import User, DoctorProfile


class HomeView(TemplateView):
    """Главная страница"""
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['slides'] = SliderImage.objects.filter(is_active=True)
        context['services'] = Service.objects.filter(is_active=True)[:6]
        context['latest_news'] = News.objects.filter(is_published=True)[:3]
        return context


class ServicesView(ListView):
    """Список услуг"""
    model = Service
    template_name = 'core/services.html'
    context_object_name = 'services'
    queryset = Service.objects.filter(is_active=True)


class DoctorsView(ListView):
    """Список врачей"""
    template_name = 'core/doctors.html'
    context_object_name = 'doctors'

    def get_queryset(self):
        return User.objects.filter(role=User.Role.DOCTOR).select_related('doctor_profile')


class DoctorDetailView(DetailView):
    """Профиль врача"""
    model = User
    template_name = 'core/doctor_detail.html'
    context_object_name = 'doctor'

    def get_queryset(self):
        return User.objects.filter(role=User.Role.DOCTOR)


class ContactsView(TemplateView):
    """Контакты"""
    template_name = 'core/contacts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clinic'] = ClinicInfo.objects.first()
        return context

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if name and email and subject and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message
            )
            messages.success(request, 'Ваше сообщение отправлено. Мы свяжемся с вами в ближайшее время.')
        else:
            messages.error(request, 'Пожалуйста, заполните все обязательные поля.')

        return redirect('core:contacts')


class NewsListView(ListView):
    """Список новостей"""
    model = News
    template_name = 'core/news_list.html'
    context_object_name = 'news_list'
    paginate_by = 9
    queryset = News.objects.filter(is_published=True)


class NewsDetailView(DetailView):
    """Детальная страница новости"""
    model = News
    template_name = 'core/news_detail.html'
    context_object_name = 'news'
    slug_field = 'slug'


class DashboardView(LoginRequiredMixin, TemplateView):
    """Панель управления"""
    template_name = 'core/dashboard.html'

    def get_template_names(self):
        user = self.request.user
        if user.is_admin:
            return ['core/dashboard_admin.html']
        elif user.is_doctor:
            return ['core/dashboard_doctor.html']
        elif user.is_nurse:
            return ['core/dashboard_nurse.html']
        elif user.is_patient:
            return ['core/dashboard_patient.html']
        return ['core/dashboard.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_doctor:
            from registry.models import Appointment
            from datetime import date
            context['today_appointments'] = Appointment.objects.filter(
                doctor=user,
                date=date.today()
            ).select_related('patient').order_by('time')
            context['appointments_count'] = Appointment.objects.filter(
                doctor=user,
                status='scheduled'
            ).count()

        elif user.is_patient:
            from registry.models import Appointment, Patient
            try:
                patient = Patient.objects.get(user=user)
                context['patient'] = patient
                context['upcoming_appointments'] = Appointment.objects.filter(
                    patient=patient,
                    status__in=['scheduled', 'confirmed']
                ).select_related('doctor').order_by('date', 'time')[:5]
            except Patient.DoesNotExist:
                context['patient'] = None

        return context

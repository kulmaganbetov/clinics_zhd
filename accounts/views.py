from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy
from .models import User


class LoginView(TemplateView):
    """Страница входа"""
    template_name = 'accounts/login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Log successful login
            from audit.models import LoginAttempt
            LoginAttempt.objects.create(
                username=username,
                ip_address=getattr(request, 'client_ip', '127.0.0.1'),
                user_agent=getattr(request, 'client_user_agent', ''),
                success=True
            )
            messages.success(request, f'Добро пожаловать, {user.get_full_name() or user.username}!')
            next_url = request.GET.get('next', 'core:dashboard')
            return redirect(next_url)
        else:
            # Log failed login
            from audit.models import LoginAttempt
            LoginAttempt.objects.create(
                username=username,
                ip_address=getattr(request, 'client_ip', '127.0.0.1'),
                user_agent=getattr(request, 'client_user_agent', ''),
                success=False,
                failure_reason='Неверный логин или пароль'
            )
            messages.error(request, 'Неверный логин или пароль')
            return render(request, self.template_name)


def logout_view(request):
    """Выход из системы"""
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('core:home')


class ProfileView(LoginRequiredMixin, TemplateView):
    """Профиль пользователя"""
    template_name = 'accounts/profile.html'


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля"""
    model = User
    template_name = 'accounts/profile_edit.html'
    fields = ['first_name', 'last_name', 'patronymic', 'email', 'phone']
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Профиль успешно обновлён')
        return super().form_valid(form)


class RegisterView(CreateView):
    """Регистрация пациента"""
    model = User
    template_name = 'accounts/register.html'
    fields = ['username', 'email', 'first_name', 'last_name', 'patronymic', 'phone', 'password']
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.role = User.Role.PATIENT
        user.save()
        messages.success(self.request, 'Регистрация прошла успешно. Теперь вы можете войти.')
        return redirect(self.success_url)

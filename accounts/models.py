from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя с ролями"""

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Администратор'
        DOCTOR = 'doctor', 'Врач'
        NURSE = 'nurse', 'Медсестра'
        PATIENT = 'patient', 'Пациент'

    role = models.CharField(
        'Роль',
        max_length=20,
        choices=Role.choices,
        default=Role.PATIENT
    )
    patronymic = models.CharField('Отчество', max_length=150, blank=True)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    iin = models.CharField('ИИН', max_length=12, blank=True, unique=True, null=True)
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    avatar = models.ImageField('Фото', upload_to='avatars/', blank=True, null=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return self.get_full_name() or self.username

    def get_full_name(self):
        parts = [self.last_name, self.first_name, self.patronymic]
        return ' '.join(filter(None, parts))

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_doctor(self):
        return self.role == self.Role.DOCTOR

    @property
    def is_nurse(self):
        return self.role == self.Role.NURSE

    @property
    def is_patient(self):
        return self.role == self.Role.PATIENT


class DoctorProfile(models.Model):
    """Профиль врача с дополнительной информацией"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='doctor_profile',
        verbose_name='Пользователь'
    )
    specialization = models.CharField('Специализация', max_length=200)
    license_number = models.CharField('Номер лицензии', max_length=50, blank=True)
    cabinet = models.CharField('Кабинет', max_length=20, blank=True)
    experience_years = models.PositiveIntegerField('Стаж (лет)', default=0)
    education = models.TextField('Образование', blank=True)
    category = models.CharField('Категория', max_length=50, blank=True)

    class Meta:
        verbose_name = 'Профиль врача'
        verbose_name_plural = 'Профили врачей'

    def __str__(self):
        return f'{self.user.get_full_name()} - {self.specialization}'


class NurseProfile(models.Model):
    """Профиль медсестры"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='nurse_profile',
        verbose_name='Пользователь'
    )
    department = models.CharField('Отделение', max_length=200)
    qualification = models.CharField('Квалификация', max_length=100, blank=True)

    class Meta:
        verbose_name = 'Профиль медсестры'
        verbose_name_plural = 'Профили медсестёр'

    def __str__(self):
        return f'{self.user.get_full_name()} - {self.department}'

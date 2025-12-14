from django.db import models
from django.conf import settings


class Patient(models.Model):
    """Пациент (прикреплённое население)"""

    class Gender(models.TextChoices):
        MALE = 'M', 'Мужской'
        FEMALE = 'F', 'Женский'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_profile',
        verbose_name='Пользователь',
        null=True, blank=True
    )
    iin = models.CharField('ИИН', max_length=12, unique=True)
    last_name = models.CharField('Фамилия', max_length=150)
    first_name = models.CharField('Имя', max_length=150)
    patronymic = models.CharField('Отчество', max_length=150, blank=True)
    birth_date = models.DateField('Дата рождения')
    gender = models.CharField('Пол', max_length=1, choices=Gender.choices)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    email = models.EmailField('Email', blank=True)
    address = models.TextField('Адрес проживания', blank=True)
    registration_address = models.TextField('Адрес прописки', blank=True)
    workplace = models.CharField('Место работы', max_length=255, blank=True)
    blood_type = models.CharField('Группа крови', max_length=10, blank=True)
    allergies = models.TextField('Аллергии', blank=True)
    chronic_diseases = models.TextField('Хронические заболевания', blank=True)
    is_attached = models.BooleanField('Прикреплён к клинике', default=True)
    attachment_date = models.DateField('Дата прикрепления', auto_now_add=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Пациент'
        verbose_name_plural = 'Пациенты'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}'.strip()

    def get_full_name(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}'.strip()

    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )


class Schedule(models.Model):
    """Расписание врача"""

    class DayOfWeek(models.IntegerChoices):
        MONDAY = 1, 'Понедельник'
        TUESDAY = 2, 'Вторник'
        WEDNESDAY = 3, 'Среда'
        THURSDAY = 4, 'Четверг'
        FRIDAY = 5, 'Пятница'
        SATURDAY = 6, 'Суббота'
        SUNDAY = 7, 'Воскресенье'

    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='Врач',
        limit_choices_to={'role': 'doctor'}
    )
    day_of_week = models.IntegerField('День недели', choices=DayOfWeek.choices)
    start_time = models.TimeField('Время начала')
    end_time = models.TimeField('Время окончания')
    slot_duration = models.PositiveIntegerField('Длительность приёма (мин)', default=15)
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписания'
        ordering = ['doctor', 'day_of_week', 'start_time']
        unique_together = ['doctor', 'day_of_week', 'start_time']

    def __str__(self):
        return f'{self.doctor} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}'


class Appointment(models.Model):
    """Талон на приём (запись)"""

    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', 'Запланирован'
        CONFIRMED = 'confirmed', 'Подтверждён'
        IN_PROGRESS = 'in_progress', 'На приёме'
        COMPLETED = 'completed', 'Завершён'
        CANCELLED = 'cancelled', 'Отменён'
        NO_SHOW = 'no_show', 'Не явился'

    class Type(models.TextChoices):
        PRIMARY = 'primary', 'Первичный'
        FOLLOW_UP = 'follow_up', 'Повторный'
        PREVENTIVE = 'preventive', 'Профилактический'
        EMERGENCY = 'emergency', 'Экстренный'

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Пациент'
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Врач',
        limit_choices_to={'role': 'doctor'}
    )
    date = models.DateField('Дата приёма')
    time = models.TimeField('Время приёма')
    end_time = models.TimeField('Время окончания', null=True, blank=True)
    appointment_type = models.CharField(
        'Тип приёма',
        max_length=20,
        choices=Type.choices,
        default=Type.PRIMARY
    )
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED
    )
    reason = models.TextField('Причина обращения', blank=True)
    notes = models.TextField('Примечания', blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_appointments',
        verbose_name='Создал'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Талон'
        verbose_name_plural = 'Талоны'
        ordering = ['date', 'time']

    def __str__(self):
        return f'Талон #{self.pk} - {self.patient} к {self.doctor} на {self.date} {self.time}'

from django.db import models
from django.conf import settings


class Department(models.Model):
    """Отделение стационара"""

    name = models.CharField('Название отделения', max_length=200)
    code = models.CharField('Код отделения', max_length=20, unique=True)
    head_doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='headed_departments',
        verbose_name='Заведующий'
    )
    beds_count = models.PositiveIntegerField('Количество коек', default=0)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    floor = models.PositiveIntegerField('Этаж', null=True, blank=True)
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Отделение'
        verbose_name_plural = 'Отделения'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def available_beds(self):
        occupied = self.beds.filter(is_occupied=True).count()
        return self.beds_count - occupied


class Bed(models.Model):
    """Койко-место"""

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='beds',
        verbose_name='Отделение'
    )
    number = models.CharField('Номер койки', max_length=20)
    ward = models.CharField('Палата', max_length=20)
    is_occupied = models.BooleanField('Занята', default=False)
    bed_type = models.CharField('Тип койки', max_length=50, blank=True)

    class Meta:
        verbose_name = 'Койка'
        verbose_name_plural = 'Койки'
        ordering = ['department', 'ward', 'number']
        unique_together = ['department', 'ward', 'number']

    def __str__(self):
        return f'Палата {self.ward}, койка {self.number}'


class Hospitalization(models.Model):
    """Госпитализация"""

    class Status(models.TextChoices):
        PLANNED = 'planned', 'Запланирована'
        ACTIVE = 'active', 'В стационаре'
        DISCHARGED = 'discharged', 'Выписан'
        TRANSFERRED = 'transferred', 'Переведён'
        DECEASED = 'deceased', 'Умер'

    class Type(models.TextChoices):
        PLANNED = 'planned', 'Плановая'
        EMERGENCY = 'emergency', 'Экстренная'
        DAY_HOSPITAL = 'day', 'Дневной стационар'

    patient = models.ForeignKey(
        'registry.Patient',
        on_delete=models.CASCADE,
        related_name='hospitalizations',
        verbose_name='Пациент'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='hospitalizations',
        verbose_name='Отделение'
    )
    bed = models.ForeignKey(
        Bed,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='hospitalizations',
        verbose_name='Койка'
    )
    attending_doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='hospitalizations',
        verbose_name='Лечащий врач'
    )
    hospitalization_type = models.CharField(
        'Тип госпитализации',
        max_length=20,
        choices=Type.choices,
        default=Type.PLANNED
    )
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED
    )
    admission_date = models.DateTimeField('Дата поступления')
    discharge_date = models.DateTimeField('Дата выписки', null=True, blank=True)
    diagnosis_admission = models.TextField('Диагноз при поступлении')
    diagnosis_code = models.CharField('Код МКБ-10', max_length=20, blank=True)
    diagnosis_clinical = models.TextField('Клинический диагноз', blank=True)
    diagnosis_final = models.TextField('Заключительный диагноз', blank=True)
    referral_source = models.CharField('Кем направлен', max_length=200, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Госпитализация'
        verbose_name_plural = 'Госпитализации'
        ordering = ['-admission_date']

    def __str__(self):
        return f'Госпитализация {self.patient} от {self.admission_date.strftime("%d.%m.%Y")}'


class MedicalHistory(models.Model):
    """История болезни"""

    hospitalization = models.OneToOneField(
        Hospitalization,
        on_delete=models.CASCADE,
        related_name='medical_history',
        verbose_name='Госпитализация'
    )
    history_number = models.CharField('Номер истории болезни', max_length=50, unique=True)
    complaints = models.TextField('Жалобы при поступлении', blank=True)
    anamnesis_morbi = models.TextField('Анамнез заболевания', blank=True)
    anamnesis_vitae = models.TextField('Анамнез жизни', blank=True)
    status_praesens = models.TextField('Объективный статус', blank=True)
    status_localis = models.TextField('Локальный статус', blank=True)
    treatment_plan = models.TextField('План лечения', blank=True)
    epicrisis = models.TextField('Эпикриз', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'История болезни'
        verbose_name_plural = 'Истории болезни'

    def __str__(self):
        return f'ИБ {self.history_number}'


class TreatmentSheet(models.Model):
    """Лист назначений"""

    hospitalization = models.ForeignKey(
        Hospitalization,
        on_delete=models.CASCADE,
        related_name='treatment_sheets',
        verbose_name='Госпитализация'
    )
    date = models.DateField('Дата')
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='treatment_sheets',
        verbose_name='Врач'
    )
    medications = models.TextField('Медикаменты', blank=True)
    procedures = models.TextField('Процедуры', blank=True)
    diet = models.CharField('Диета', max_length=100, blank=True)
    regime = models.CharField('Режим', max_length=100, blank=True)
    notes = models.TextField('Примечания', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Лист назначений'
        verbose_name_plural = 'Листы назначений'
        ordering = ['-date']

    def __str__(self):
        return f'Лист назначений от {self.date}'


class TemperatureSheet(models.Model):
    """Температурный лист"""

    hospitalization = models.ForeignKey(
        Hospitalization,
        on_delete=models.CASCADE,
        related_name='temperature_sheets',
        verbose_name='Госпитализация'
    )
    datetime = models.DateTimeField('Дата и время')
    temperature = models.DecimalField('Температура', max_digits=4, decimal_places=1, null=True, blank=True)
    blood_pressure_sys = models.PositiveIntegerField('АД систолическое', null=True, blank=True)
    blood_pressure_dia = models.PositiveIntegerField('АД диастолическое', null=True, blank=True)
    pulse = models.PositiveIntegerField('Пульс', null=True, blank=True)
    respiratory_rate = models.PositiveIntegerField('ЧДД', null=True, blank=True)
    weight = models.DecimalField('Вес', max_digits=5, decimal_places=2, null=True, blank=True)
    diuresis = models.PositiveIntegerField('Диурез (мл)', null=True, blank=True)
    stool = models.CharField('Стул', max_length=50, blank=True)
    fluid_intake = models.PositiveIntegerField('Выпито жидкости (мл)', null=True, blank=True)
    nurse = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='temperature_sheets',
        verbose_name='Медсестра'
    )
    notes = models.TextField('Примечания', blank=True)

    class Meta:
        verbose_name = 'Температурный лист'
        verbose_name_plural = 'Температурные листы'
        ordering = ['-datetime']

    def __str__(self):
        return f'Т-лист {self.hospitalization.patient} от {self.datetime}'


class DischargeEpicrisis(models.Model):
    """Выписной эпикриз"""

    hospitalization = models.OneToOneField(
        Hospitalization,
        on_delete=models.CASCADE,
        related_name='discharge_epicrisis',
        verbose_name='Госпитализация'
    )
    discharge_date = models.DateField('Дата выписки')
    days_in_hospital = models.PositiveIntegerField('Койко-дней')
    diagnosis_main = models.TextField('Основной диагноз')
    diagnosis_concomitant = models.TextField('Сопутствующий диагноз', blank=True)
    diagnosis_complications = models.TextField('Осложнения', blank=True)
    treatment_summary = models.TextField('Проведённое лечение')
    condition_at_discharge = models.TextField('Состояние при выписке')
    recommendations = models.TextField('Рекомендации')
    sick_leave_info = models.TextField('Данные о больничном листе', blank=True)
    follow_up_date = models.DateField('Дата контрольного осмотра', null=True, blank=True)
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='discharge_epicrises',
        verbose_name='Лечащий врач'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Выписной эпикриз'
        verbose_name_plural = 'Выписные эпикризы'

    def __str__(self):
        return f'Эпикриз {self.hospitalization.patient}'

from django.db import models
from django.conf import settings


class MedicalRecord(models.Model):
    """Электронная медицинская карта (ЭМК)"""

    patient = models.OneToOneField(
        'registry.Patient',
        on_delete=models.CASCADE,
        related_name='medical_record',
        verbose_name='Пациент'
    )
    card_number = models.CharField('Номер карты', max_length=50, unique=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Медицинская карта'
        verbose_name_plural = 'Медицинские карты'

    def __str__(self):
        return f'ЭМК {self.card_number} - {self.patient}'


class Examination(models.Model):
    """Осмотр пациента"""

    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name='examinations',
        verbose_name='Медицинская карта'
    )
    appointment = models.OneToOneField(
        'registry.Appointment',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='examination',
        verbose_name='Приём'
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='examinations',
        verbose_name='Врач'
    )
    date = models.DateTimeField('Дата осмотра', auto_now_add=True)

    # Жалобы и анамнез
    complaints = models.TextField('Жалобы', blank=True)
    anamnesis = models.TextField('Анамнез заболевания', blank=True)
    life_anamnesis = models.TextField('Анамнез жизни', blank=True)

    # Объективный осмотр
    general_condition = models.CharField('Общее состояние', max_length=100, blank=True)
    consciousness = models.CharField('Сознание', max_length=100, blank=True)
    skin = models.TextField('Кожные покровы', blank=True)
    lymph_nodes = models.TextField('Лимфатические узлы', blank=True)
    respiratory_system = models.TextField('Органы дыхания', blank=True)
    cardiovascular_system = models.TextField('Сердечно-сосудистая система', blank=True)
    digestive_system = models.TextField('Органы пищеварения', blank=True)
    urinary_system = models.TextField('Мочевыделительная система', blank=True)
    nervous_system = models.TextField('Нервная система', blank=True)
    musculoskeletal_system = models.TextField('Опорно-двигательный аппарат', blank=True)

    # Витальные показатели
    temperature = models.DecimalField('Температура', max_digits=4, decimal_places=1, null=True, blank=True)
    blood_pressure_sys = models.PositiveIntegerField('АД систолическое', null=True, blank=True)
    blood_pressure_dia = models.PositiveIntegerField('АД диастолическое', null=True, blank=True)
    pulse = models.PositiveIntegerField('Пульс', null=True, blank=True)
    respiratory_rate = models.PositiveIntegerField('ЧДД', null=True, blank=True)
    weight = models.DecimalField('Вес (кг)', max_digits=5, decimal_places=2, null=True, blank=True)
    height = models.DecimalField('Рост (см)', max_digits=5, decimal_places=1, null=True, blank=True)

    # Заключение
    diagnosis_preliminary = models.TextField('Предварительный диагноз', blank=True)
    diagnosis_main = models.TextField('Основной диагноз', blank=True)
    diagnosis_code = models.CharField('Код МКБ-10', max_length=20, blank=True)
    diagnosis_concomitant = models.TextField('Сопутствующий диагноз', blank=True)
    recommendations = models.TextField('Рекомендации', blank=True)

    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Осмотр'
        verbose_name_plural = 'Осмотры'
        ordering = ['-date']

    def __str__(self):
        return f'Осмотр {self.medical_record.patient} от {self.date.strftime("%d.%m.%Y")}'


class Prescription(models.Model):
    """Назначение (лекарства, процедуры)"""

    class Type(models.TextChoices):
        MEDICATION = 'medication', 'Лекарственное средство'
        PROCEDURE = 'procedure', 'Процедура'
        CONSULTATION = 'consultation', 'Консультация'
        DIET = 'diet', 'Диета'
        REGIME = 'regime', 'Режим'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Активно'
        COMPLETED = 'completed', 'Выполнено'
        CANCELLED = 'cancelled', 'Отменено'

    examination = models.ForeignKey(
        Examination,
        on_delete=models.CASCADE,
        related_name='prescriptions',
        verbose_name='Осмотр'
    )
    prescription_type = models.CharField(
        'Тип назначения',
        max_length=20,
        choices=Type.choices
    )
    name = models.CharField('Наименование', max_length=255)
    dosage = models.CharField('Дозировка', max_length=100, blank=True)
    frequency = models.CharField('Частота приёма', max_length=100, blank=True)
    duration = models.CharField('Длительность', max_length=100, blank=True)
    route = models.CharField('Способ применения', max_length=100, blank=True)
    instructions = models.TextField('Инструкции', blank=True)
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    start_date = models.DateField('Дата начала', null=True, blank=True)
    end_date = models.DateField('Дата окончания', null=True, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Назначение'
        verbose_name_plural = 'Назначения'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_prescription_type_display()}: {self.name}'


class ExaminationTemplate(models.Model):
    """Шаблон осмотра для врача (ВОП/терапевт)"""

    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='examination_templates',
        verbose_name='Врач',
        null=True, blank=True
    )
    name = models.CharField('Название шаблона', max_length=200)
    specialization = models.CharField('Специализация', max_length=100, blank=True)
    complaints = models.TextField('Жалобы', blank=True)
    anamnesis = models.TextField('Анамнез', blank=True)
    examination_plan = models.TextField('План осмотра', blank=True)
    diagnosis_template = models.TextField('Шаблон диагноза', blank=True)
    recommendations_template = models.TextField('Шаблон рекомендаций', blank=True)
    is_public = models.BooleanField('Публичный шаблон', default=False)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Шаблон осмотра'
        verbose_name_plural = 'Шаблоны осмотров'
        ordering = ['name']

    def __str__(self):
        return self.name

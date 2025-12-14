from django.db import models
from django.conf import settings


class ReportType(models.Model):
    """Тип отчёта"""

    class Category(models.TextChoices):
        MEDICAL = 'medical', 'Медицинские'
        FINANCIAL = 'financial', 'Финансовые'
        STATISTICAL = 'statistical', 'Статистические'
        OPERATIONAL = 'operational', 'Операционные'
        KPI = 'kpi', 'KPI'

    name = models.CharField('Название отчёта', max_length=200)
    code = models.CharField('Код', max_length=50, unique=True)
    category = models.CharField('Категория', max_length=20, choices=Category.choices)
    description = models.TextField('Описание', blank=True)
    template_path = models.CharField('Путь к шаблону', max_length=255, blank=True)
    sql_query = models.TextField('SQL запрос', blank=True)
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Тип отчёта'
        verbose_name_plural = 'Типы отчётов'
        ordering = ['category', 'name']

    def __str__(self):
        return self.name


class GeneratedReport(models.Model):
    """Сгенерированный отчёт"""

    class Format(models.TextChoices):
        PDF = 'pdf', 'PDF'
        EXCEL = 'excel', 'Excel'
        CSV = 'csv', 'CSV'
        HTML = 'html', 'HTML'

    report_type = models.ForeignKey(
        ReportType,
        on_delete=models.CASCADE,
        related_name='generated_reports',
        verbose_name='Тип отчёта'
    )
    name = models.CharField('Название', max_length=255)
    period_start = models.DateField('Начало периода', null=True, blank=True)
    period_end = models.DateField('Конец периода', null=True, blank=True)
    parameters = models.JSONField('Параметры', default=dict, blank=True)
    format = models.CharField('Формат', max_length=10, choices=Format.choices, default=Format.PDF)
    file = models.FileField('Файл', upload_to='reports/', null=True, blank=True)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='generated_reports',
        verbose_name='Сгенерировал'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Сгенерированный отчёт'
        verbose_name_plural = 'Сгенерированные отчёты'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} от {self.created_at.strftime("%d.%m.%Y")}'


class KPIIndicator(models.Model):
    """KPI показатель"""

    class IndicatorType(models.TextChoices):
        VISITS = 'visits', 'Посещения'
        HOSPITALIZATIONS = 'hospitalizations', 'Госпитализации'
        LAB_TESTS = 'lab_tests', 'Лабораторные исследования'
        RADIOLOGY = 'radiology', 'Радиологические исследования'
        REVENUE = 'revenue', 'Выручка'
        PATIENT_SATISFACTION = 'satisfaction', 'Удовлетворённость пациентов'
        WAIT_TIME = 'wait_time', 'Время ожидания'
        BED_OCCUPANCY = 'bed_occupancy', 'Загрузка коек'

    name = models.CharField('Название показателя', max_length=200)
    code = models.CharField('Код', max_length=50, unique=True)
    indicator_type = models.CharField('Тип показателя', max_length=20, choices=IndicatorType.choices)
    description = models.TextField('Описание', blank=True)
    unit = models.CharField('Единица измерения', max_length=50)
    target_value = models.DecimalField('Целевое значение', max_digits=15, decimal_places=2, null=True, blank=True)
    calculation_method = models.TextField('Методика расчёта', blank=True)
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'KPI показатель'
        verbose_name_plural = 'KPI показатели'
        ordering = ['name']

    def __str__(self):
        return self.name


class KPIValue(models.Model):
    """Значение KPI"""

    indicator = models.ForeignKey(
        KPIIndicator,
        on_delete=models.CASCADE,
        related_name='values',
        verbose_name='Показатель'
    )
    period_start = models.DateField('Начало периода')
    period_end = models.DateField('Конец периода')
    value = models.DecimalField('Значение', max_digits=15, decimal_places=2)
    department = models.CharField('Отделение', max_length=200, blank=True)
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='kpi_values',
        verbose_name='Врач'
    )
    notes = models.TextField('Примечания', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Значение KPI'
        verbose_name_plural = 'Значения KPI'
        ordering = ['-period_end']

    def __str__(self):
        return f'{self.indicator} - {self.value} ({self.period_start} - {self.period_end})'

    @property
    def achievement_percent(self):
        if self.indicator.target_value and self.indicator.target_value != 0:
            return (self.value / self.indicator.target_value) * 100
        return None


class Registry(models.Model):
    """Реестр оказанных услуг"""

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Черновик'
        FORMED = 'formed', 'Сформирован'
        SENT = 'sent', 'Отправлен'
        ACCEPTED = 'accepted', 'Принят'
        REJECTED = 'rejected', 'Отклонён'

    name = models.CharField('Название реестра', max_length=255)
    period_start = models.DateField('Начало периода')
    period_end = models.DateField('Конец периода')
    status = models.CharField('Статус', max_length=20, choices=Status.choices, default=Status.DRAFT)
    total_services = models.PositiveIntegerField('Всего услуг', default=0)
    total_amount = models.DecimalField('Общая сумма', max_digits=15, decimal_places=2, default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_registries',
        verbose_name='Создал'
    )
    sent_date = models.DateTimeField('Дата отправки', null=True, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Реестр'
        verbose_name_plural = 'Реестры'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.period_start} - {self.period_end})'


class RegistryItem(models.Model):
    """Позиция реестра"""

    registry = models.ForeignKey(
        Registry,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Реестр'
    )
    patient = models.ForeignKey(
        'registry.Patient',
        on_delete=models.CASCADE,
        related_name='registry_items',
        verbose_name='Пациент'
    )
    service_date = models.DateField('Дата услуги')
    service_code = models.CharField('Код услуги', max_length=50)
    service_name = models.CharField('Наименование услуги', max_length=255)
    diagnosis_code = models.CharField('Код МКБ-10', max_length=20)
    quantity = models.PositiveIntegerField('Количество', default=1)
    price = models.DecimalField('Цена', max_digits=12, decimal_places=2)
    amount = models.DecimalField('Сумма', max_digits=12, decimal_places=2)
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='registry_services',
        verbose_name='Врач'
    )

    class Meta:
        verbose_name = 'Позиция реестра'
        verbose_name_plural = 'Позиции реестра'

    def __str__(self):
        return f'{self.service_name} - {self.patient}'

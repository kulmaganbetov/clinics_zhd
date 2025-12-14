from django.db import models
from django.conf import settings


class LabTestType(models.Model):
    """Тип лабораторного исследования"""

    class Category(models.TextChoices):
        CLINICAL = 'clinical', 'Клинические'
        BIOCHEMICAL = 'biochemical', 'Биохимические'
        HORMONAL = 'hormonal', 'Гормональные'
        IMMUNOLOGICAL = 'immunological', 'Иммунологические'
        MICROBIOLOGICAL = 'microbiological', 'Микробиологические'
        CYTOLOGICAL = 'cytological', 'Цитологические'
        GENETIC = 'genetic', 'Генетические'

    name = models.CharField('Название', max_length=200)
    code = models.CharField('Код', max_length=50, unique=True)
    category = models.CharField('Категория', max_length=20, choices=Category.choices)
    description = models.TextField('Описание', blank=True)
    unit = models.CharField('Единицы измерения', max_length=50, blank=True)
    normal_range = models.CharField('Норма', max_length=100, blank=True)
    preparation = models.TextField('Подготовка к исследованию', blank=True)
    turnaround_time = models.PositiveIntegerField('Срок выполнения (часов)', default=24)
    price = models.DecimalField('Стоимость', max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Тип исследования'
        verbose_name_plural = 'Типы исследований'
        ordering = ['category', 'name']

    def __str__(self):
        return f'{self.code} - {self.name}'


class LabOrder(models.Model):
    """Направление на лабораторное исследование"""

    class Status(models.TextChoices):
        CREATED = 'created', 'Создано'
        SAMPLE_COLLECTED = 'sample_collected', 'Биоматериал собран'
        IN_PROGRESS = 'in_progress', 'В работе'
        COMPLETED = 'completed', 'Выполнено'
        CANCELLED = 'cancelled', 'Отменено'

    class Priority(models.TextChoices):
        ROUTINE = 'routine', 'Плановое'
        URGENT = 'urgent', 'Срочное'
        STAT = 'stat', 'Cito!'

    patient = models.ForeignKey(
        'registry.Patient',
        on_delete=models.CASCADE,
        related_name='lab_orders',
        verbose_name='Пациент'
    )
    ordering_doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ordered_lab_tests',
        verbose_name='Направивший врач'
    )
    test_type = models.ForeignKey(
        LabTestType,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Тип исследования'
    )
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=Status.choices,
        default=Status.CREATED
    )
    priority = models.CharField(
        'Приоритет',
        max_length=20,
        choices=Priority.choices,
        default=Priority.ROUTINE
    )
    clinical_info = models.TextField('Клиническая информация', blank=True)
    diagnosis = models.CharField('Диагноз', max_length=255, blank=True)
    order_date = models.DateTimeField('Дата направления', auto_now_add=True)
    sample_date = models.DateTimeField('Дата забора', null=True, blank=True)
    completion_date = models.DateTimeField('Дата выполнения', null=True, blank=True)

    class Meta:
        verbose_name = 'Направление на исследование'
        verbose_name_plural = 'Направления на исследования'
        ordering = ['-order_date']

    def __str__(self):
        return f'{self.test_type} для {self.patient}'


class LabResult(models.Model):
    """Результат лабораторного исследования"""

    order = models.OneToOneField(
        LabOrder,
        on_delete=models.CASCADE,
        related_name='result',
        verbose_name='Направление'
    )
    value = models.CharField('Результат', max_length=255)
    unit = models.CharField('Единицы', max_length=50, blank=True)
    reference_range = models.CharField('Референсный диапазон', max_length=100, blank=True)
    is_abnormal = models.BooleanField('Отклонение от нормы', default=False)
    interpretation = models.TextField('Интерпретация', blank=True)
    comments = models.TextField('Комментарии', blank=True)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='performed_lab_tests',
        verbose_name='Выполнил'
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='verified_lab_tests',
        verbose_name='Подтвердил'
    )
    result_date = models.DateTimeField('Дата результата', auto_now_add=True)

    class Meta:
        verbose_name = 'Результат исследования'
        verbose_name_plural = 'Результаты исследований'

    def __str__(self):
        return f'Результат: {self.order.test_type}'


class RadiologyStudyType(models.Model):
    """Тип радиологического исследования (РИС)"""

    class Modality(models.TextChoices):
        XRAY = 'xray', 'Рентген'
        CT = 'ct', 'КТ'
        MRI = 'mri', 'МРТ'
        US = 'us', 'УЗИ'
        MAMMO = 'mammo', 'Маммография'
        FLUORO = 'fluoro', 'Флюорография'
        ANGIO = 'angio', 'Ангиография'

    name = models.CharField('Название', max_length=200)
    code = models.CharField('Код', max_length=50, unique=True)
    modality = models.CharField('Модальность', max_length=20, choices=Modality.choices)
    body_part = models.CharField('Область исследования', max_length=100)
    description = models.TextField('Описание', blank=True)
    preparation = models.TextField('Подготовка', blank=True)
    contraindications = models.TextField('Противопоказания', blank=True)
    duration = models.PositiveIntegerField('Длительность (минут)', default=15)
    price = models.DecimalField('Стоимость', max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Тип радиологического исследования'
        verbose_name_plural = 'Типы радиологических исследований'
        ordering = ['modality', 'name']

    def __str__(self):
        return f'{self.get_modality_display()} - {self.name}'


class RadiologyOrder(models.Model):
    """Направление на радиологическое исследование"""

    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', 'Запланировано'
        IN_PROGRESS = 'in_progress', 'Выполняется'
        COMPLETED = 'completed', 'Выполнено'
        DESCRIBED = 'described', 'Описано'
        CANCELLED = 'cancelled', 'Отменено'

    patient = models.ForeignKey(
        'registry.Patient',
        on_delete=models.CASCADE,
        related_name='radiology_orders',
        verbose_name='Пациент'
    )
    ordering_doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ordered_radiology_studies',
        verbose_name='Направивший врач'
    )
    study_type = models.ForeignKey(
        RadiologyStudyType,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Тип исследования'
    )
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED
    )
    priority = models.CharField(
        'Приоритет',
        max_length=20,
        choices=LabOrder.Priority.choices,
        default=LabOrder.Priority.ROUTINE
    )
    clinical_info = models.TextField('Клиническая информация', blank=True)
    diagnosis = models.CharField('Диагноз', max_length=255, blank=True)
    scheduled_date = models.DateTimeField('Дата назначена', null=True, blank=True)
    performed_date = models.DateTimeField('Дата выполнения', null=True, blank=True)
    order_date = models.DateTimeField('Дата направления', auto_now_add=True)

    class Meta:
        verbose_name = 'Направление на рад. исследование'
        verbose_name_plural = 'Направления на рад. исследования'
        ordering = ['-order_date']

    def __str__(self):
        return f'{self.study_type} для {self.patient}'


class RadiologyResult(models.Model):
    """Результат радиологического исследования"""

    order = models.OneToOneField(
        RadiologyOrder,
        on_delete=models.CASCADE,
        related_name='result',
        verbose_name='Направление'
    )
    findings = models.TextField('Протокол исследования')
    conclusion = models.TextField('Заключение')
    recommendations = models.TextField('Рекомендации', blank=True)
    radiologist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='radiology_reports',
        verbose_name='Врач-рентгенолог'
    )
    report_date = models.DateTimeField('Дата заключения', auto_now_add=True)

    class Meta:
        verbose_name = 'Результат рад. исследования'
        verbose_name_plural = 'Результаты рад. исследований'

    def __str__(self):
        return f'Заключение: {self.order.study_type}'


class DicomStudy(models.Model):
    """DICOM исследование"""

    radiology_order = models.ForeignKey(
        RadiologyOrder,
        on_delete=models.CASCADE,
        related_name='dicom_studies',
        verbose_name='Направление'
    )
    study_instance_uid = models.CharField('Study Instance UID', max_length=128, unique=True)
    study_date = models.DateTimeField('Дата исследования')
    accession_number = models.CharField('Accession Number', max_length=64, blank=True)
    modality = models.CharField('Модальность', max_length=20)
    description = models.CharField('Описание', max_length=255, blank=True)
    number_of_series = models.PositiveIntegerField('Количество серий', default=0)
    number_of_images = models.PositiveIntegerField('Количество изображений', default=0)
    storage_path = models.CharField('Путь к файлам', max_length=500, blank=True)
    pacs_url = models.URLField('URL в PACS', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'DICOM исследование'
        verbose_name_plural = 'DICOM исследования'
        ordering = ['-study_date']

    def __str__(self):
        return f'DICOM {self.study_instance_uid}'

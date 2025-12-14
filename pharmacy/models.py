from django.db import models
from django.conf import settings


class DrugCategory(models.Model):
    """Категория лекарственных средств"""

    name = models.CharField('Название', max_length=200)
    code = models.CharField('Код', max_length=20, unique=True)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Категория препаратов'
        verbose_name_plural = 'Категории препаратов'
        ordering = ['name']

    def __str__(self):
        return self.name


class Drug(models.Model):
    """Лекарственное средство"""

    class DrugType(models.TextChoices):
        ESSENTIAL = 'essential', 'ЖНВЛП'
        REGULAR = 'regular', 'Обычное'
        NARCOTIC = 'narcotic', 'Наркотическое'
        PSYCHOTROPIC = 'psychotropic', 'Психотропное'

    name = models.CharField('Торговое название', max_length=255)
    inn = models.CharField('МНН (INN)', max_length=255, blank=True)
    category = models.ForeignKey(
        DrugCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='drugs',
        verbose_name='Категория'
    )
    drug_type = models.CharField(
        'Тип препарата',
        max_length=20,
        choices=DrugType.choices,
        default=DrugType.REGULAR
    )
    form = models.CharField('Форма выпуска', max_length=100)
    dosage = models.CharField('Дозировка', max_length=100)
    manufacturer = models.CharField('Производитель', max_length=255, blank=True)
    country = models.CharField('Страна', max_length=100, blank=True)
    barcode = models.CharField('Штрих-код', max_length=50, blank=True)
    atc_code = models.CharField('Код АТХ', max_length=20, blank=True)
    description = models.TextField('Описание', blank=True)
    contraindications = models.TextField('Противопоказания', blank=True)
    storage_conditions = models.CharField('Условия хранения', max_length=255, blank=True)
    is_prescription = models.BooleanField('По рецепту', default=False)
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Лекарственное средство'
        verbose_name_plural = 'Лекарственные средства'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} {self.dosage} {self.form}'


class Warehouse(models.Model):
    """Склад"""

    name = models.CharField('Название', max_length=200)
    code = models.CharField('Код', max_length=20, unique=True)
    location = models.CharField('Расположение', max_length=255, blank=True)
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='warehouses',
        verbose_name='Ответственный'
    )
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склады'
        ordering = ['name']

    def __str__(self):
        return self.name


class DrugStock(models.Model):
    """Остатки на складе"""

    drug = models.ForeignKey(
        Drug,
        on_delete=models.CASCADE,
        related_name='stocks',
        verbose_name='Препарат'
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='stocks',
        verbose_name='Склад'
    )
    batch_number = models.CharField('Номер партии', max_length=100)
    quantity = models.PositiveIntegerField('Количество')
    unit = models.CharField('Единица измерения', max_length=20, default='шт')
    purchase_price = models.DecimalField('Цена закупки', max_digits=12, decimal_places=2)
    selling_price = models.DecimalField('Цена продажи', max_digits=12, decimal_places=2, null=True, blank=True)
    manufacture_date = models.DateField('Дата производства', null=True, blank=True)
    expiry_date = models.DateField('Срок годности')
    received_date = models.DateField('Дата поступления', auto_now_add=True)
    supplier = models.CharField('Поставщик', max_length=255, blank=True)
    invoice_number = models.CharField('Номер накладной', max_length=100, blank=True)

    class Meta:
        verbose_name = 'Остатки'
        verbose_name_plural = 'Остатки на складе'
        ordering = ['expiry_date']

    def __str__(self):
        return f'{self.drug} - {self.quantity} {self.unit}'

    @property
    def is_expired(self):
        from datetime import date
        return self.expiry_date < date.today()

    @property
    def days_until_expiry(self):
        from datetime import date
        return (self.expiry_date - date.today()).days


class StockMovement(models.Model):
    """Движение товара"""

    class MovementType(models.TextChoices):
        RECEIPT = 'receipt', 'Приход'
        ISSUE = 'issue', 'Расход'
        TRANSFER = 'transfer', 'Перемещение'
        WRITE_OFF = 'write_off', 'Списание'
        RETURN = 'return', 'Возврат'

    drug = models.ForeignKey(
        Drug,
        on_delete=models.CASCADE,
        related_name='movements',
        verbose_name='Препарат'
    )
    movement_type = models.CharField(
        'Тип движения',
        max_length=20,
        choices=MovementType.choices
    )
    warehouse_from = models.ForeignKey(
        Warehouse,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='movements_out',
        verbose_name='Склад-источник'
    )
    warehouse_to = models.ForeignKey(
        Warehouse,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='movements_in',
        verbose_name='Склад-получатель'
    )
    quantity = models.PositiveIntegerField('Количество')
    batch_number = models.CharField('Номер партии', max_length=100, blank=True)
    document_number = models.CharField('Номер документа', max_length=100, blank=True)
    reason = models.TextField('Основание', blank=True)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stock_movements',
        verbose_name='Выполнил'
    )
    created_at = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Движение товара'
        verbose_name_plural = 'Движения товаров'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_movement_type_display()} - {self.drug} ({self.quantity})'


class DrugRequest(models.Model):
    """Заявка на препараты"""

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Черновик'
        SUBMITTED = 'submitted', 'Подана'
        APPROVED = 'approved', 'Одобрена'
        REJECTED = 'rejected', 'Отклонена'
        FULFILLED = 'fulfilled', 'Выполнена'

    department = models.CharField('Отделение/подразделение', max_length=200)
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='drug_requests',
        verbose_name='Заявитель'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='approved_drug_requests',
        verbose_name='Утвердил'
    )
    notes = models.TextField('Примечания', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Заявка на препараты'
        verbose_name_plural = 'Заявки на препараты'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заявка #{self.pk} от {self.department}'


class DrugRequestItem(models.Model):
    """Позиция заявки"""

    request = models.ForeignKey(
        DrugRequest,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заявка'
    )
    drug = models.ForeignKey(
        Drug,
        on_delete=models.CASCADE,
        related_name='request_items',
        verbose_name='Препарат'
    )
    quantity_requested = models.PositiveIntegerField('Запрошено')
    quantity_approved = models.PositiveIntegerField('Одобрено', null=True, blank=True)
    quantity_issued = models.PositiveIntegerField('Выдано', null=True, blank=True)

    class Meta:
        verbose_name = 'Позиция заявки'
        verbose_name_plural = 'Позиции заявки'

    def __str__(self):
        return f'{self.drug} - {self.quantity_requested}'

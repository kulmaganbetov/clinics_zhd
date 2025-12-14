from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    """Журнал аудита"""

    class Action(models.TextChoices):
        CREATE = 'create', 'Создание'
        READ = 'read', 'Просмотр'
        UPDATE = 'update', 'Изменение'
        DELETE = 'delete', 'Удаление'
        LOGIN = 'login', 'Вход'
        LOGOUT = 'logout', 'Выход'
        FAILED_LOGIN = 'failed_login', 'Неудачный вход'
        EXPORT = 'export', 'Экспорт'
        PRINT = 'print', 'Печать'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        verbose_name='Пользователь'
    )
    action = models.CharField('Действие', max_length=20, choices=Action.choices)
    model_name = models.CharField('Модель', max_length=100, blank=True)
    object_id = models.PositiveIntegerField('ID объекта', null=True, blank=True)
    object_repr = models.CharField('Объект', max_length=255, blank=True)
    changes = models.JSONField('Изменения', default=dict, blank=True)
    ip_address = models.GenericIPAddressField('IP адрес', null=True, blank=True)
    user_agent = models.TextField('User Agent', blank=True)
    url = models.URLField('URL', max_length=500, blank=True)
    timestamp = models.DateTimeField('Дата и время', auto_now_add=True)

    class Meta:
        verbose_name = 'Запись аудита'
        verbose_name_plural = 'Журнал аудита'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['model_name', 'object_id']),
        ]

    def __str__(self):
        return f'{self.user} - {self.get_action_display()} - {self.timestamp}'


class AccessLog(models.Model):
    """Журнал доступа к медицинским данным"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='access_logs',
        verbose_name='Пользователь'
    )
    patient = models.ForeignKey(
        'registry.Patient',
        on_delete=models.SET_NULL,
        null=True,
        related_name='access_logs',
        verbose_name='Пациент'
    )
    resource_type = models.CharField('Тип ресурса', max_length=100)
    resource_id = models.PositiveIntegerField('ID ресурса', null=True, blank=True)
    access_type = models.CharField('Тип доступа', max_length=50)
    reason = models.TextField('Причина доступа', blank=True)
    ip_address = models.GenericIPAddressField('IP адрес', null=True, blank=True)
    timestamp = models.DateTimeField('Дата и время', auto_now_add=True)

    class Meta:
        verbose_name = 'Доступ к мед. данным'
        verbose_name_plural = 'Доступы к мед. данным'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['patient', 'timestamp']),
        ]

    def __str__(self):
        return f'{self.user} -> {self.patient} ({self.resource_type})'


class LoginAttempt(models.Model):
    """Попытка входа"""

    username = models.CharField('Имя пользователя', max_length=150)
    ip_address = models.GenericIPAddressField('IP адрес')
    user_agent = models.TextField('User Agent', blank=True)
    success = models.BooleanField('Успешно', default=False)
    failure_reason = models.CharField('Причина неудачи', max_length=255, blank=True)
    timestamp = models.DateTimeField('Дата и время', auto_now_add=True)

    class Meta:
        verbose_name = 'Попытка входа'
        verbose_name_plural = 'Попытки входа'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['username', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]

    def __str__(self):
        status = 'Успешно' if self.success else 'Неудачно'
        return f'{self.username} - {status} - {self.timestamp}'


class DataExportLog(models.Model):
    """Журнал экспорта данных"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='export_logs',
        verbose_name='Пользователь'
    )
    export_type = models.CharField('Тип экспорта', max_length=100)
    description = models.TextField('Описание', blank=True)
    records_count = models.PositiveIntegerField('Количество записей', default=0)
    file_format = models.CharField('Формат файла', max_length=20, blank=True)
    ip_address = models.GenericIPAddressField('IP адрес', null=True, blank=True)
    timestamp = models.DateTimeField('Дата и время', auto_now_add=True)

    class Meta:
        verbose_name = 'Экспорт данных'
        verbose_name_plural = 'Экспорты данных'
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.user} - {self.export_type} - {self.timestamp}'

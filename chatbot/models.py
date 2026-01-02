from django.db import models
from django.conf import settings


class ChatSession(models.Model):
    """Сессия чата"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Пользователь'
    )
    session_key = models.CharField('Ключ сессии', max_length=255, blank=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Сессия чата'
        verbose_name_plural = 'Сессии чата'
        ordering = ['-updated_at']

    def __str__(self):
        if self.user:
            return f"Чат {self.user.get_full_name() or self.user.username}"
        return f"Чат (гость) - {self.session_key[:8]}"


class ChatMessage(models.Model):
    """Сообщение в чате"""
    class Role(models.TextChoices):
        USER = 'user', 'Пользователь'
        ASSISTANT = 'assistant', 'Ассистент'
        SYSTEM = 'system', 'Система'

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Сессия'
    )
    role = models.CharField('Роль', max_length=20, choices=Role.choices)
    content = models.TextField('Содержание')
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.get_role_display()}: {self.content[:50]}..."

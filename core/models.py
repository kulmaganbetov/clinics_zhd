from django.db import models


class ClinicInfo(models.Model):
    """Информация о клинике"""

    name = models.CharField('Название', max_length=255, default='Железнодорожная клиника')
    short_name = models.CharField('Краткое название', max_length=100, blank=True)
    city = models.CharField('Город', max_length=100, default='Кокшетау')
    address = models.TextField('Адрес')
    phone = models.CharField('Телефон', max_length=50)
    phone_emergency = models.CharField('Телефон экстренной помощи', max_length=50, blank=True)
    email = models.EmailField('Email', blank=True)
    website = models.URLField('Веб-сайт', blank=True)
    license_number = models.CharField('Номер лицензии', max_length=100, blank=True)
    bin = models.CharField('БИН', max_length=12, blank=True)
    working_hours = models.TextField('Часы работы', blank=True)
    description = models.TextField('Описание', blank=True)
    logo = models.ImageField('Логотип', upload_to='clinic/', blank=True, null=True)

    class Meta:
        verbose_name = 'Информация о клинике'
        verbose_name_plural = 'Информация о клинике'

    def __str__(self):
        return self.name


class SliderImage(models.Model):
    """Изображения для слайдера"""

    title = models.CharField('Заголовок', max_length=200, blank=True)
    subtitle = models.CharField('Подзаголовок', max_length=255, blank=True)
    image = models.ImageField('Изображение', upload_to='slider/')
    link = models.URLField('Ссылка', blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Изображение слайдера'
        verbose_name_plural = 'Изображения слайдера'
        ordering = ['order']

    def __str__(self):
        return self.title or f'Слайд #{self.pk}'


class Service(models.Model):
    """Услуга клиники"""

    name = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    icon = models.CharField('Иконка (CSS класс)', max_length=50, blank=True)
    image = models.ImageField('Изображение', upload_to='services/', blank=True, null=True)
    price = models.DecimalField('Цена', max_digits=12, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField('Активно', default=True)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class News(models.Model):
    """Новости клиники"""

    title = models.CharField('Заголовок', max_length=255)
    slug = models.SlugField('URL', unique=True)
    content = models.TextField('Содержание')
    excerpt = models.TextField('Краткое описание', max_length=500, blank=True)
    image = models.ImageField('Изображение', upload_to='news/', blank=True, null=True)
    is_published = models.BooleanField('Опубликовано', default=False)
    published_at = models.DateTimeField('Дата публикации', null=True, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    """Сообщение обратной связи"""

    name = models.CharField('Имя', max_length=150)
    email = models.EmailField('Email')
    phone = models.CharField('Телефон', max_length=20, blank=True)
    subject = models.CharField('Тема', max_length=200)
    message = models.TextField('Сообщение')
    is_read = models.BooleanField('Прочитано', default=False)
    created_at = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.subject}'

from django.utils.deprecation import MiddlewareMixin


class AuditMiddleware(MiddlewareMixin):
    """Middleware для логирования действий пользователей"""

    def process_request(self, request):
        # Сохраняем IP и User Agent для использования в моделях
        request.client_ip = self.get_client_ip(request)
        request.client_user_agent = request.META.get('HTTP_USER_AGENT', '')

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

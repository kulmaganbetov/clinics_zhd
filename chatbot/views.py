import json
import os
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from openai import OpenAI
from .models import ChatSession, ChatMessage


# Системный промпт с информацией о клинике
SYSTEM_PROMPT = """Вы - Аяла, виртуальный медицинский ассистент Кокшетауской железнодорожной больницы.
Ваше имя - Аяла. Всегда представляйтесь этим именем при приветствии.
Ваша задача - помогать пациентам с информацией об услугах клиники, отвечать на вопросы о симптомах и заболеваниях,
а также предоставлять общие медицинские консультации.

ИНФОРМАЦИЯ О КЛИНИКЕ:

ТОО «Кокшетауская железнодорожная больница»
Адрес: г. Кокшетау, ул. Абая, 161 «А»
E-mail: kfmst@mail.ru
Instagram: @kzhb.kokshetau

Контактные телефоны:
- Приемная: +7 (7162) 76-11-11
- Главный врач: +7 (7162) 72-12-93
- Регистратура: +7 (7162) 29-47-70
- Приемный покой: +7 (7162) 29-34-68
- Аптека: +7 (7162) 33-59-19

УСЛУГИ КЛИНИКИ:
- Поликлиническое обслуживание (терапия, хирургия, кардиология, неврология, офтальмология, ЛОР, урология, гинекология и др.)
- Стационарное лечение
- Лабораторная диагностика
- Инструментальная диагностика (УЗИ, ЭКГ, рентген, КТ, МРТ)
- Физиотерапия и реабилитация
- Дневной стационар
- Скорая медицинская помощь
- Профилактические осмотры

ВАЖНЫЕ ПРАВИЛА:
1. Всегда будьте вежливы и профессиональны
2. При серьёзных симптомах рекомендуйте обратиться к врачу или вызвать скорую помощь
3. Не ставьте диагнозы - только информируйте о возможных причинах симптомов
4. При необходимости направляйте в нужное отделение клиники
5. Отвечайте на русском языке
6. Если вопрос не связан с медициной или клиникой, вежливо объясните, что вы специализируетесь на медицинских консультациях

Приветствуйте пользователей дружелюбно и предлагайте свою помощь!"""


class ChatView(View):
    """Страница чата"""

    def get(self, request):
        return render(request, 'chatbot/chat.html')


@method_decorator(csrf_exempt, name='dispatch')
class ChatAPIView(View):
    """API для обработки сообщений чата"""

    def post(self, request):
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            session_id = data.get('session_id')

            if not user_message:
                return JsonResponse({'error': 'Сообщение не может быть пустым'}, status=400)

            # Получаем или создаём сессию
            chat_session = self._get_or_create_session(request, session_id)

            # Сохраняем сообщение пользователя
            ChatMessage.objects.create(
                session=chat_session,
                role=ChatMessage.Role.USER,
                content=user_message
            )

            # Получаем историю сообщений для контекста
            messages = self._build_messages(chat_session)

            # Отправляем запрос к OpenAI
            response_text = self._get_ai_response(messages)

            # Сохраняем ответ ассистента
            ChatMessage.objects.create(
                session=chat_session,
                role=ChatMessage.Role.ASSISTANT,
                content=response_text
            )

            return JsonResponse({
                'response': response_text,
                'session_id': chat_session.id
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный формат данных'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Произошла ошибка: {str(e)}'}, status=500)

    def _get_or_create_session(self, request, session_id=None):
        """Получает или создаёт сессию чата"""
        if session_id:
            try:
                return ChatSession.objects.get(id=session_id)
            except ChatSession.DoesNotExist:
                pass

        # Создаём новую сессию
        session = ChatSession(
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key or ''
        )
        session.save()
        return session

    def _build_messages(self, chat_session):
        """Строит список сообщений для OpenAI API"""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Добавляем последние 20 сообщений из истории
        history = chat_session.messages.order_by('-created_at')[:20]
        for msg in reversed(list(history)):
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        return messages

    def _get_ai_response(self, messages):
        """Получает ответ от OpenAI API"""
        api_key = os.environ.get('OPENAI_API_KEY')

        if not api_key:
            return "К сожалению, сервис временно недоступен. Пожалуйста, позвоните нам по телефону: +7 (7162) 76-11-11"

        try:
            client = OpenAI(api_key=api_key)

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Извините, произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже или позвоните нам: +7 (7162) 76-11-11"


class ClearChatView(View):
    """Очистка истории чата"""

    def post(self, request):
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')

            if session_id:
                ChatSession.objects.filter(id=session_id).delete()

            return JsonResponse({'status': 'ok'})
        except:
            return JsonResponse({'status': 'ok'})

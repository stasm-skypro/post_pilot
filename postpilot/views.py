import logging

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
    DeleteView,
    TemplateView,
)

from .forms import RecipientForm, MessageForm, MailingForm, SendAttemptForm
from .models import Recipient, Message, Mailing, SendAttempt
from .services import send_mailing

logger = logging.getLogger(__name__)


# -- Welcome view --
class WelcomeView(TemplateView):
    """
    View для отображения страницы приглашения.
    """

    template_name = "welcome.html"


# -- Home view --
class HomeView(TemplateView):
    """
    View для отображения главной страницы.
    """

    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mailings"] = Mailing.objects.all()  # Все рассылки
        context["mailings_started"] = Mailing.objects.filter(status="started")  # Только активные рассылки
        context["recipients"] = Recipient.objects.all()  # Получатели
        return context


# -- Recipient views --
class RecipientCreateView(CreateView):
    """
    View для создания нового получателя.
    """

    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("postpilot:recipient_list")

    def form_valid(self, form):
        """Дополнительная обработка перед сохранением формы."""
        self.object = form.save()  # Сохраняем объект формы в базу
        logger.info(
            f"Получатель рассылки успешно создан. Имя получателя: '{self.object.full_name}'. Email: '{self.object.email}'"
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        """Обработка в случае неверной формы."""
        logger.warning("Ошибка при создании получателя рассылки: {form.errors}")
        return super().form_invalid(form)


class RecipientListView(ListView):
    """
    View для отображения списка получателей.
    """

    model = Recipient
    form_class = RecipientForm
    context_object_name = "recipients"


class RecipientUpdateView(UpdateView):
    """
    View для редактирования получателя.
    """

    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("postpilot:recipient_list")

    def form_valid(self, form):
        """Дополнительная обработка перед сохранением формы."""
        self.object = form.save()  # Сохраняем объект формы в базу
        logger.info(
            "Получатель рассылки успешно обновлен. Имя: '{self.object.full_name}'. Email: '{self.object.email}'"
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        """Обработка в случае неверной формы."""
        logger.warning(f"Ошибка при обновлении получателя рассылки: {form.errors}")
        return super().form_invalid(form)


class RecipientDeleteView(DeleteView):
    """
    View для удаления получателя.
    """

    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("postpilot:recipient_list")

    def post(self, request, *args, **kwargs):
        """Переопределение метода POST для вызова delete."""
        logger.info("Удаление получателя рассылки через POST-запрос.")
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """Переопределение метода delete для логирования."""
        recipient = self.get_object()
        logger.info(
            f"Получатель рассылки успешно удалён. Имя получателя: '{recipient.full_name}'. Email: '{recipient.email}'"
        )
        return super().delete(request, *args, **kwargs)


# -- Message views --
class MessageCreateView(CreateView):
    """
    View для создания нового сообщения.
    """

    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("postpilot:message_list")

    def form_valid(self, form):
        """Дополнительная обработка перед сохранением формы."""
        self.object = form.save()  # Сохраняем объект формы в базу
        logger.info(f"Сообщение успешно создано. Тема: '{self.object.subject}'. Текст: '{self.object.body_text}'")
        return super().form_valid(form)

    def form_invalid(self, form):
        """Обработка в случае неверной формы."""
        logger.warning(f"Ошибка при создании сообщения: {form.errors}")
        return super().form_invalid(form)


class MessageListView(ListView):
    """
    View для отображения списка сообщений.
    """

    model = Message
    form_class = MessageForm
    context_object_name = "messages"


class MessageUpdateView(UpdateView):
    """
    View для редактирования сообщения.
    """

    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("postpilot:message_list")

    def form_valid(self, form):
        """Дополнительная обработка перед сохранением формы."""
        self.object = form.save()  # Сохраняем объект формы в базу
        logger.info(f"Сообщение успешно обновлено. Тема: '{self.object.subject}'. Текст: '{self.object.body_text}'")
        return super().form_valid(form)

    def form_invalid(self, form):
        """Обработка в случае неверной формы."""
        logger.warning(f"Ошибка при обновлении сообщения: {form.errors}")
        return super().form_invalid(form)


class MessageDeleteView(DeleteView):
    """
    View для удаления сообщения.
    """

    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("postpilot:message_list")

    def post(self, request, *args, **kwargs):
        """Переопределение метода POST для вызова delete."""
        logger.info("Удаление сообщения через POST-запрос.")
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """Переопределение метода delete для логирования."""
        message = self.get_object()
        logger.info(f"Сообщение успешно удалено. Тема: '{message.subject}'. Текст: '{message.body_text}'")
        return super().delete(request, *args, **kwargs)


# -- Mailing views --
class MailingCreateView(CreateView):
    """
    View для создания рассылки.
    """

    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("postpilot:mailing_list")

    def form_valid(self, form):
        """Дополнительная обработка перед сохранением формы."""
        self.object = form.save()  # Сохраняем объект формы в базу
        logger.info(
            f"Рассылка успешно создана. Статус рассылки: '{self.object.status}'. Сообщение: '{self.object.message}'"
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        """Обработка в случае неверной формы."""
        logger.warning(f"Ошибка при создании рассылки: {form.errors}")
        return super().form_invalid(form)


class MailingListView(ListView):
    """
    View для отображения списка рассылок.
    """

    model = Mailing
    form_class = MailingForm
    context_object_name = "mailings"

    def get_context_data(self, **kwargs):
        """
        Добавляем переменную в контекст для отображения количества рассылок со статусом "started".
        """
        context = super().get_context_data(**kwargs)
        # context["started_count"] = sum(1 for mailing in self.object_list if mailing.status == "started")  # Можно сразу передать  в контекст количество активных рассылок
        context["mailings_started"] = Mailing.objects.filter(status="started")
        return context


class MailingUpdateView(UpdateView):
    """
    View для редактирования рассылки.
    """

    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("postpilot:mailing_list")

    def form_valid(self, form):
        """Дополнительная обработка перед сохранением формы."""
        self.object = form.save()  # Сохраняем объект формы в базу
        logger.info(
            f"Рассылка успешно обновлена. Статус рассылки: '{self.object.status}'. Сообщение: '{self.object.message}'"
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        """Обработка в случае неверной формы."""
        logger.warning(f"Ошибка при обновлении рассылки: {form.errors}")
        return super().form_invalid(form)


class MailingDeleteView(DeleteView):
    """
    View для удаления рассылки.
    """

    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("postpilot:mailing_list")

    def post(self, request, *args, **kwargs):
        """Переопределение метода POST для вызова delete."""
        logger.info("Удаление рассылки через POST-запрос.")
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """Переопределение метода delete для логирования."""
        mailing = self.get_object()
        logger.info(f"Рассылка успешно удалена. Статус рассылки: '{mailing.status}'. Сообщение: '{mailing.message}'")
        return super().delete(request, *args, **kwargs)


# -- SendAttempt views --
class SendAttemptCreateView(CreateView):
    """
    View для создания попытки рассылки.
    """

    model = SendAttempt
    form_class = SendAttemptForm
    success_url = reverse_lazy("postpilot:mailing_list")

    def form_valid(self, form):
        """Дополнительная обработка перед сохранением формы."""
        self.object = form.save()  # Сохраняем объект формы в базу
        logger.info("Попытка рассылки успешно создана.")
        return super().form_valid(form)

    def form_invalid(self, form):
        """Обработка в случае неверной формы."""
        logger.warning(f"Ошибка при попытке рассылки: {form.errors}")
        return super().form_invalid(form)


class SendAttemptView(View):
    """
    View для запуска попытки рассылки.
    """

    def post(self, request, pk):
        """
        Переопределение метода POST для запуска попытки рассылки.
        """
        mailing = get_object_or_404(Mailing, pk=pk)

        try:
            send_mailing(mailing)  # Вызов сервисной функции
            messages.success(request, f"Рассылка '{mailing}' успешно отправлена!")
        except Exception as e:
            messages.error(request, f"Ошибка при отправке рассылки: {e}")

        return redirect("postpilot:mailing_list")


class SendAttemptUpdateView(UpdateView):
    """
    View для редактирования попытки рассылки.
    """

    model = SendAttempt
    form_class = SendAttemptForm
    success_url = reverse_lazy("postpilot:mailing_list")

    def form_valid(self, form):
        """Дополнительная обработка перед сохранением формы."""
        self.object = form.save()  # Сохраняем объект формы в базу
        logger.info("Попытка рассылки успешно обновлена.")
        return super().form_valid(form)

    def form_invalid(self, form):
        """Обработка в случае неверной формы."""
        logger.warning(f"Ошибка при обновлении попытки рассылки: {form.errors}")
        return super().form_invalid(form)


class SendAttemptDeleteView(DeleteView):
    """
    View для удаления попытки рассылки.
    """

    model = SendAttempt
    form_class = SendAttemptForm
    success_url = reverse_lazy("postpilot:mailing_list")

    def post(self, request, *args, **kwargs):
        """Переопределение метода POST для вызова delete."""
        logger.info("Удаление попытки рассылки через POST-запрос.")
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """Переопределение метода delete для логирования."""
        send_attempt = self.get_object()
        logger.info(f"Попытка рассылки успешно удалена. Статус: '{send_attempt.status}'")
        return super().delete(request, *args, **kwargs)

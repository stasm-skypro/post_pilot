import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
    DeleteView,
    TemplateView,
)

from core.mixins import OwnerRequiredMixin, IsManagerOrOwnerListMixin
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

    def get_context_data(self, **kwargs):
        """Добавляем переменную в контекст для отображения количества рассылок."""
        context = super().get_context_data(**kwargs)
        context["mailings"] = Mailing.objects.all()  # Все рассылки
        context["mailings_started"] = Mailing.objects.filter(status="started")  # Только активные рассылки
        context["recipients"] = Recipient.objects.all()  # Получатели

        return context


# -- Home view --
@method_decorator(cache_page(60 * 15), name="dispatch")
class HomeView(UserPassesTestMixin, OwnerRequiredMixin, TemplateView):
    """
    View для отображения главной страницы.
    """

    template_name = "home.html"

    def test_func(self):
        """Метод для проверки прав доступа."""
        user = self.request.user
        return user.groups.filter(name="Менеджеры").exists() or user.is_authenticated

    def get_context_data(self, **kwargs):
        """Добавляем переменную в контекст для отображения количества рассылок со статусом "started"."""
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.groups.filter(name="Менеджеры").exists():  # Фильтруем объекты только для менеджера
            context["mailings"] = Mailing.objects.all()
            context["mailings_started"] = Mailing.objects.filter(status="started")
            context["recipients"] = Recipient.objects.all()
            context["send_attempts"] = SendAttempt.objects.all()
        elif user.is_authenticated:  # Фильтруем объекты только для владельца
            context["mailings"] = Mailing.objects.filter(owner=user)
            context["mailings_started"] = Mailing.objects.filter(owner=user, status="started")
            context["recipients"] = Recipient.objects.filter(owner=user)
            context["send_attempts"] = SendAttempt.objects.filter(owner=user)
        else:  # Остальные не видят ничего
            context["mailings"] = Mailing.objects.none()
            context["mailings_started"] = Mailing.objects.none()
            context["recipients"] = Recipient.objects.none()
            context["send_attempts"] = SendAttempt.objects.none()

        return context


# -- Recipient views --
class RecipientCreateView(OwnerRequiredMixin, CreateView):
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
        form.instance.owner = self.request.user  # Устанавливаем текущего пользователя владельцем
        logger.info(f"Владелец рассылки - {self.request.user}")
        return super().form_valid(form)

    def form_invalid(self, form):
        """Обработка в случае неверной формы."""
        logger.warning("Ошибка при создании получателя рассылки: {form.errors}")
        return super().form_invalid(form)


class RecipientListView(IsManagerOrOwnerListMixin, ListView):
    """
    View для отображения списка получателей.
    """

    model = Recipient
    form_class = RecipientForm
    context_object_name = "recipients"


class RecipientUpdateView(OwnerRequiredMixin, UpdateView):
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
        logger.info(f"Владелец рассылки - {self.request.user}")
        return super().form_valid(form)

    def form_invalid(self, form):
        """Обработка в случае неверной формы."""
        logger.warning(f"Ошибка при обновлении получателя рассылки: {form.errors}")
        return super().form_invalid(form)


class RecipientDeleteView(OwnerRequiredMixin, DeleteView):
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
        logger.info(f"Владелец рассылки - {self.request.user}")
        return super().delete(request, *args, **kwargs)


# -- Message views --
class MessageCreateView(OwnerRequiredMixin, CreateView):
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
        form.instance.owner = self.request.user  # Устанавливаем текущего пользователя владельцем
        logger.info(f"Владелец рассылки - {self.request.user}")
        return super().form_valid(form)

    def form_invalid(self, form):
        """Обработка в случае неверной формы."""
        logger.warning(f"Ошибка при создании сообщения: {form.errors}")
        return super().form_invalid(form)


class MessageListView(IsManagerOrOwnerListMixin, ListView):
    """
    View для отображения списка сообщений.
    """

    model = Message
    form_class = MessageForm
    context_object_name = "messages"


class MessageUpdateView(OwnerRequiredMixin, UpdateView):
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
        logger.info(f"Владелец рассылки - {self.request.user}")
        return super().form_valid(form)

    def form_invalid(self, form):
        """Обработка в случае неверной формы."""
        logger.warning(f"Ошибка при обновлении сообщения: {form.errors}")
        return super().form_invalid(form)


class MessageDeleteView(OwnerRequiredMixin, DeleteView):
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
        logger.info(f"Владелец рассылки - {self.request.user}")
        return super().delete(request, *args, **kwargs)


# -- Mailing views --
class MailingCreateView(OwnerRequiredMixin, CreateView):
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
        form.instance.owner = self.request.user  # Устанавливаем текущего пользователя владельцем
        logger.info(f"Владелец рассылки - {self.request.user}")
        return super().form_valid(form)

    def form_invalid(self, form):
        """Обработка в случае неверной формы."""
        logger.warning(f"Ошибка при создании рассылки: {form.errors}")
        return super().form_invalid(form)


class MailingListView(IsManagerOrOwnerListMixin, ListView):
    """
    View для отображения списка рассылок.
    """

    model = Mailing
    form_class = MailingForm
    context_object_name = "mailings"


class MailingUpdateView(OwnerRequiredMixin, UpdateView):
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
        logger.info(f"Владелец рассылки - {self.request.user}")
        return super().form_valid(form)

    def form_invalid(self, form):
        """Обработка в случае неверной формы."""
        logger.warning(f"Ошибка при обновлении рассылки: {form.errors}")
        return super().form_invalid(form)


class MailingDeleteView(OwnerRequiredMixin, DeleteView):
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
        logger.info(f"Владелец рассылки - {self.request.user}")
        return super().delete(request, *args, **kwargs)


# -- SendAttempt views --
class SendAttemptCreateView(OwnerRequiredMixin, CreateView):
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
        form.instance.owner = self.request.user  # Устанавливаем текущего пользователя владельцем
        logger.info(f"Владелец рассылки - {self.request.user}")
        return super().form_valid(form)

    def form_invalid(self, form):
        """Обработка в случае неверной формы."""
        logger.warning(f"Ошибка при попытке рассылки: {form.errors}")
        return super().form_invalid(form)


class SendAttemptView(OwnerRequiredMixin, View):
    """
    View для запуска попытки рассылки.
    """

    def post(self, request, pk):
        """Переопределение метода POST для запуска попытки рассылки."""
        mailing = get_object_or_404(Mailing, pk=pk)

        try:
            send_mailing(mailing)  # Вызов сервисной функции
            messages.success(request, f"Рассылка '{mailing}' успешно отправлена!")
        except Exception as e:
            messages.error(request, f"Ошибка при отправке рассылки: {e}")

        return redirect("postpilot:mailing_list")


class SendAttemptListView(IsManagerOrOwnerListMixin, ListView):
    """
    View для отображения списка попыток рассылки.
    """

    model = SendAttempt
    form_class = SendAttemptForm
    context_object_name = "send_attempts"


class SendAttemptUpdateView(OwnerRequiredMixin, UpdateView):
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
        logger.info(f"Владелец рассылки - {self.request.user}")
        return super().form_valid(form)

    def form_invalid(self, form):
        """Обработка в случае неверной формы."""
        logger.warning(f"Ошибка при обновлении попытки рассылки: {form.errors}")
        return super().form_invalid(form)


class SendAttemptDeleteView(OwnerRequiredMixin, DeleteView):
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
        logger.info(f"Владелец рассылки - {self.request.user}")
        return super().delete(request, *args, **kwargs)


class StopAttemptView(LoginRequiredMixin, View):
    """
    View для остановки попытки отправки рассылки, если она запущена.
    """

    def post(self, request, pk, *args, **kwargs):
        mailing = get_object_or_404(Mailing, id=pk)

        # Проверяем, является ли пользователь владельцем рассылки
        if mailing.owner != request.user:
            messages.error(request, "Вы не можете остановить эту рассылку.")
            logger.error("Пользователь не является владельцем рассылки.")
            return redirect("postpilot:mailing_list")

        # Проверяем, что рассылка находится в статусе "started"
        if mailing.status != "started":
            messages.warning(request, "Эта рассылка не находится в активном состоянии.")
            logger.warning("Рассылка не находится в активном состоянии.")
            return redirect("postpilot:mailing_list")

        # Останавливаем рассылку
        mailing.status = "broken"
        mailing.save()

        messages.success(request, "Рассылка успешно остановлена.")
        logger.info("Рассылка успешно остановлена.")
        return redirect("postpilot:mailing_list")

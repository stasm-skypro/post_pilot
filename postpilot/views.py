from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, TemplateView

from .models import Recipient, Message, Mailing


class WelcomeView(TemplateView):
    """
    View для отображения страницы приглашения.
    """

    template_name = "welcome.html"


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


class RecipientCreateView(CreateView):
    """
    View для создания нового получателя.
    """

    model = Recipient
    fields = "__all__"
    success_url = reverse_lazy("home")


class RecipientListView(ListView):
    """
    View для отображения списка получателей.
    """

    model = Recipient
    fields = "__all__"
    context_object_name = "recipients"
    success_url = reverse_lazy("home")


class RecipientUpdateView(UpdateView):
    """
    View для редактирования получателя.
    """

    model = Recipient
    fields = "__all__"
    success_url = reverse_lazy("home")


class RecipientDeleteView(DeleteView):
    """
    View для удаления получателя.
    """

    model = Recipient
    fields = "__all__"
    success_url = reverse_lazy("home")


class MessageCreateView(CreateView):
    """
    View для создания нового сообщения.
    """

    model = Message
    fields = "__all__"
    success_url = reverse_lazy("home")


class MessageListView(ListView):
    """
    View для отображения списка сообщений.
    """

    model = Message
    fields = "__all__"
    context_object_name = "messages"
    success_url = reverse_lazy("home")


class MessageUpdateView(UpdateView):
    """
    View для редактирования сообщения.
    """

    model = Message
    fields = "__all__"
    success_url = reverse_lazy("home")


class MessageDeleteView(DeleteView):
    """
    View для удаления сообщения.
    """

    model = Message
    fields = "__all__"
    success_url = reverse_lazy("home")


class MailingCreateView(CreateView):
    """
    View для создания рассылки.
    """

    model = Mailing
    fields = "__all__"
    success_url = reverse_lazy("home")


class MailingListView(ListView):
    """
    View для отображения списка рассылок.
    """

    model = Mailing
    fields = "__all__"
    context_object_name = "mailings"
    success_url = reverse_lazy("home")

    def get_context_data(self, **kwargs):
        """
        Добавляем переменную в контекст для отображения количества рассылок со статусом "started".
        """
        context = super().get_context_data(**kwargs)
        # context["started_count"] = sum(1 for mailing in self.object_list if mailing.status == "started")
        context["mailings_started"] = Mailing.objects.filter(status="started")
        return context


class MailingUpdateView(UpdateView):
    """
    View для редактирования рассылки.
    """

    model = Mailing
    fields = "__all__"
    success_url = reverse_lazy("home")


class MailingDeleteView(DeleteView):
    """
    View для удаления рассылки.
    """

    model = Mailing
    fields = "__all__"
    success_url = reverse_lazy("home")


class SendAttemptListView(CreateView):
    """
    View для отображения списка попыток отправки.
    """

    model = Mailing
    fields = "__all__"
    context_object_name = "send_attempts"
    success_url = reverse_lazy("home")

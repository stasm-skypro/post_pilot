from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, TemplateView

from .models import Recipient, Message, Mailing


class HomeView(TemplateView):
    """
    View для отображения главной страницы.
    """

    template_name = "home.html"


class RecipientCreateView(CreateView):
    """
    View для создания нового получателя.
    """

    model = Recipient
    fields = "__all__"
    success_url = reverse_lazy("recipient_list")


class RecipientListView(ListView):
    """
    View для отображения списка получателей.
    """

    model = Recipient
    fields = "__all__"
    context_object_name = "recipients"
    success_url = reverse_lazy("recipient_list")


class RecipientUpdateView(UpdateView):
    """
    View для редактирования получателя.
    """

    model = Recipient
    fields = "__all__"
    success_url = reverse_lazy("recipient_list")


class RecipientDeleteView(DeleteView):
    """
    View для удаления получателя.
    """

    model = Recipient
    fields = "__all__"
    success_url = reverse_lazy("recipient_list")


class MessageCreateView(CreateView):
    """
    View для создания нового сообщения.
    """

    model = Message
    fields = "__all__"
    success_url = reverse_lazy("recipient_list")


class MessageListView(ListView):
    """
    View для отображения списка сообщений.
    """

    model = Message
    fields = "__all__"
    context_object_name = "messages"
    success_url = reverse_lazy("recipient_list")


class MessageUpdateView(UpdateView):
    """
    View для редактирования сообщения.
    """

    model = Message
    fields = "__all__"
    success_url = reverse_lazy("recipient_list")


class MessageDeleteView(DeleteView):
    """
    View для удаления сообщения.
    """

    model = Message
    fields = "__all__"
    success_url = reverse_lazy("recipient_list")


class MailingCreateView(CreateView):
    """
    View для создания рассылки.
    """

    model = Mailing
    fields = "__all__"
    success_url = reverse_lazy("recipient_list")


class MailingListView(ListView):
    """
    View для отображения списка рассылок.
    """

    model = Mailing
    fields = "__all__"
    context_object_name = "mailings"
    success_url = reverse_lazy("recipient_list")


class MailingUpdateView(UpdateView):
    """
    View для редактирования рассылки.
    """

    model = Mailing
    fields = "__all__"
    success_url = reverse_lazy("recipient_list")


class MailingDeleteView(DeleteView):
    """
    View для удаления рассылки.
    """

    model = Mailing
    fields = "__all__"
    success_url = reverse_lazy("recipient_list")


class SendAttemptListView(CreateView):
    """
    View для отображения списка попыток отправки.
    """

    model = Mailing
    fields = "__all__"
    context_object_name = "send_attempts"
    success_url = reverse_lazy("recipient_list")

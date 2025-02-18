from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView

from .models import Recipient


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

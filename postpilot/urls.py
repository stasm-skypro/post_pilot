from django.urls import path

from .apps import PostpilotConfig
from .views import (
    WelcomeView,
    HomeView,
    MailingCreateView,
    MailingListView,
    MailingUpdateView,
    MailingDeleteView,
    RecipientCreateView,
    RecipientListView,
    RecipientUpdateView,
    RecipientDeleteView,
    MessageListView,
    MessageCreateView,
    MessageUpdateView,
    MessageDeleteView,
    SendAttemptCreateView,
    SendAttemptView,
    StopAttemptView,
)

app_name = PostpilotConfig.name

urlpatterns = [
    # -- welcome section --
    path("", WelcomeView.as_view(), name="welcome"),  # Стартовая страница приложения
    # -- home section --
    path("home/", HomeView.as_view(), name="home"),  # Главная страница приложения
    #
    # -- mailing section --
    path("mailing_form/", MailingCreateView.as_view(), name="mailing_create"),  # Форма создания рассылки
    path("mailing_list", MailingListView.as_view(), name="mailing_list"),  # Список рассылок подробный
    path(
        "mailing_form/<int:pk>/", MailingUpdateView.as_view(), name="mailing_update"
    ),  # Форма редактирования рассылки
    path(
        "mailing_confirm_delete/<int:pk>/delete/",
        MailingDeleteView.as_view(),
        name="mailing_delete",
    ),  # Форма удаления рассылки
    #
    # -- recipient section --
    path("recipient_form/", RecipientCreateView.as_view(), name="recipient_create"),  # Форма для создания пользователя
    path("recipient_list/", RecipientListView.as_view(), name="recipient_list"),  # Список пользователей
    path(
        "recipient_form/<int:pk>/",
        RecipientUpdateView.as_view(),
        name="recipient_update",
    ),  # Форма редактирования пользователя
    path(
        "recipient_confirm_delete/<int:pk>/delete/",
        RecipientDeleteView.as_view(),
        name="recipient_delete",
    ),  # Форма удаления пользователя
    #
    # -- message section --
    path("message_form/", MessageCreateView.as_view(), name="message_create"),  # Форма создания сообщения
    path("message_list/", MessageListView.as_view(), name="message_list"),  # Список сообщений
    path(
        "message_form/<int:pk>/", MessageUpdateView.as_view(), name="message_update"
    ),  # Форма редактирования сообщения
    path(
        "message_confirm_delete/<int:pk>/delete/",
        MessageDeleteView.as_view(),
        name="message_delete",
    ),  # Форма удаления сообщения
    #
    # -- send attempt section --
    path(
        "sendattempt_form/", SendAttemptCreateView.as_view(), name="sendattempt_create"
    ),  # Форма создания попытки рассылки
    path(
        "sendattempt/<int:pk>/send/", SendAttemptView.as_view(), name="sendattempt"
    ),  # Форма запуска попытки рассылки
    path(
        "sendattempt/<int:pk>/stop/", StopAttemptView.as_view(), name="stopattempt"
    ),  # Форма остановки попытки рассылки
]

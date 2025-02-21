from django.urls import path

from .apps import PostpilotConfig
from .views import WelcomeView, HomeView, MailingCreateView, MailingListView, RecipientCreateView, MailingUpdateView, \
    MailingDeleteView

app_name = PostpilotConfig.name

urlpatterns = [
    # -- mailing section --
    path("", WelcomeView.as_view(), name="welcome"),  # Стартовая страница приложения
    path("home/", HomeView.as_view(), name="home"),   # Главная страница приложения
    path("mailing_form/", MailingCreateView.as_view(), name="mailing_create"),  # Форма создания рассылки
    path("mailing_list", MailingListView.as_view(), name="mailing_list"),  # Список рассылок подробный
    path("mailing_form/<int:pk>/", MailingUpdateView.as_view(), name="mailing_update"),  # Форма редактирования рассылки
    path("mailing_confirm_delete/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"),  # Форма удаления рассылки
    # -- recipient section --
    path("recipient_form/", RecipientCreateView.as_view(), name="recipient_create")  # Форма для создания пользователя
]

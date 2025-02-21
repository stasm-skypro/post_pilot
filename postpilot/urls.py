from django.urls import path

from .apps import PostpilotConfig
from .views import HomeView, WelcomeView, MailingCreateView

app_name = PostpilotConfig.name

urlpatterns = [
    path("", WelcomeView.as_view(), name="welcome"),  # Стартовая страница приложения
    path("home/", HomeView.as_view(), name="home"),   # Главная страница приложения
    path("mailing_form/", MailingCreateView.as_view(), name="mailing_create"),  # Форма создания рассылки
]

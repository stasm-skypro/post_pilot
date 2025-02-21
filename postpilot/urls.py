from django.urls import path

from .apps import PostpilotConfig
from .views import HomeView, WelcomeView, MailingListView

app_name = PostpilotConfig.name

urlpatterns = [
    path("", WelcomeView.as_view(), name="welcome"),  # Стартовая страница приложения
    path("home/", HomeView.as_view(), name="home"),   # Главная страница приложения
    path("mailings/", MailingListView.as_view(), name="mailing_list"),
]

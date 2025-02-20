from django.urls import path

from .apps import PostpilotConfig
from .views import HomeView, WelcomeView

app_name = PostpilotConfig.name

urlpatterns = [
    path("", WelcomeView.as_view(), name="welcome"),  # Главная страница приложения
    path("home/", HomeView.as_view(), name="home"),
]

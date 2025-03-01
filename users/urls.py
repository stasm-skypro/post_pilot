from django.urls import path

from .apps import UsersConfig

app_name = UsersConfig.name

urlpatterns = [
    path("register/", CustomUserRegisterView.as_view(), name="register"),
]

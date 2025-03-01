from django.urls import path

from .apps import UsersConfig
from .views import CustomUserRegisterView, CustomUserLoginView, CustomUserLogoutView, CustomUserUpdateView

app_name = UsersConfig.name

urlpatterns = [
    path("register/", CustomUserRegisterView.as_view(), name="profile"),  # регистрация
    path("login/", CustomUserLoginView.as_view(), name="login"),  # авторизация
    path("logout/", CustomUserLogoutView.as_view(), name="logout"),  # выход
    path("user/<int:pk>/update/", CustomUserUpdateView.as_view(), name="update"), # редактирование
]

from django.urls import path

from .apps import UsersConfig
from .views import CustomUserRegisterView, CustomUserLoginView, CustomUserUpdateView, custom_logout

app_name = UsersConfig.name

urlpatterns = [
    path("register/", CustomUserRegisterView.as_view(), name="profile"),  # регистрация
    path("login/", CustomUserLoginView.as_view(), name="login"),  # авторизация
    # path("logout/", CustomUserLogoutView.as_view(), name="logout"),  # выход
    path("logout/", custom_logout, name="logout"),
    path("user/<int:pk>/update/", CustomUserUpdateView.as_view(), name="update"), # редактирование
]

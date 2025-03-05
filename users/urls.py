from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from .apps import UsersConfig
from .views import (
    CustomUserRegisterView,
    CustomUserLoginView,
    CustomUserUpdateView,
    custom_logout,
    CustomUserListView,
    CustomUserBlockView,
)

app_name = UsersConfig.name

urlpatterns = [
    # -- Регистрация пользователя --
    path("register/", CustomUserRegisterView.as_view(), name="profile"),  # регистрация
    path("login/", CustomUserLoginView.as_view(), name="login"),  # авторизация
    # path("logout/", CustomUserLogoutView.as_view(), name="logout"),  # выход
    path("logout/", custom_logout, name="logout"),
    path("user/<int:pk>/update/", CustomUserUpdateView.as_view(), name="update"),  # редактирование
    # -- Сброс пароля --
    # Django по умолчанию связывает password_reset/ с admin/password_reset/, поэтому нужно явно
    # указывать путь к password_reset/ и ко всем остальным шаблонам.
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="users/password_reset_form.html",
            success_url=reverse_lazy("users:password_reset_done"),
            email_template_name="users/password_reset_email.html",
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            success_url=reverse_lazy("users:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"),
        name="password_reset_complete",
    ),
    path("users_list/", CustomUserListView.as_view(), name="users_list"),
    path("block/<int:user_id>/", CustomUserBlockView.as_view(), name="block_user"),
]

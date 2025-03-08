import logging

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.generic import CreateView, UpdateView, ListView

from core.mixins import IsManagerOrOwnerListMixin
from users.forms import CustomUserRegisterForm
from users.models import CustomUser

logger = logging.getLogger(__name__)


@method_decorator(csrf_protect, name="dispatch")
class CustomUserRegisterView(CreateView):
    """
    Представление для регистрации нового пользователя.
    """

    model = CustomUser
    form_class = CustomUserRegisterForm
    template_name = "users/profile.html"
    success_url = reverse_lazy("postpilot:welcome")

    @staticmethod
    def send_welcome_email(user_email):
        """
        Отправляет сообщение на email пользователя при успешной регистрации.
        """
        subject = "Добро пожаловать на сайт!"
        message = "Спасибо за регистрацию! Мы рады видеть вас среди нас."
        from_email = "stasm226@gmail.com"
        recipients = [user_email]
        send_mail(subject, message, from_email, recipients)
        logger.info(f"Отправка электронного письма пользователю {user_email} после успешной регистрации.")

    def form_valid(self, form):
        """
        Переопределение метода для сохранения пользователя в базе данных и отправки уведомления.
        """
        user = form.save()  # Сохраняем пользователя в базе данных

        # Указываем backend, если он не определился
        user.backend = "django.contrib.auth.backends.ModelBackend"

        login(self.request, user)  # Автоматически аутентифицирует пользователя сразу после успешной регистрации

        logger.info(f"Пользователь {user.email} успешно зарегистрирован.")
        self.send_welcome_email(user.email)
        logger.info(f"Приветственное письмо пользователю {user.email} отправлено.")

        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Переопределение метода для обработки неверной формы регистрации.
        """
        logger.error(f"Ошибка при регистрации пользователя: {form.errors}.")
        return super().form_invalid(form)


class CustomUserLoginView(LoginView):
    """
    Представление для авторизации пользователя.
    """

    template_name = "users/login.html"
    context_object_name = "user"

    def get_success_url(self):
        """
        Переопределение метода для перенаправления пользователя после успешной авторизации.
        """
        logger.info(f"Пользователь {self.request.user.email} успешно авторизован.")
        return reverse_lazy("postpilot:welcome")


class CustomUserListView(IsManagerOrOwnerListMixin, ListView):
    """
    Представление для отображения списка пользователей.
    """

    model = CustomUser
    template_name = "users/users_list.html"
    context_object_name = "users"


class CustomUserBlockView(IsManagerOrOwnerListMixin, View):
    """
    Контроллер для блокировки и разблокировки пользователя.
    Доступен только менеджерам.
    """

    def test_func(self):
        """Проверяет, является ли пользователь менеджером."""
        return self.request.user.groups.filter(name="Менеджеры").exists()

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST-запрос для блокировки/разблокировки пользователя."""
        user = get_object_or_404(CustomUser, id=kwargs["user_id"])

        if user.is_active:
            user.is_active = False
            logger.info(f"Пользователь {user.email} заблокирован.")
            messages.success(request, f"Пользователь {user.email} заблокирован.")
        else:
            user.is_active = True
            logger.info(f"Пользователь {user.email} разблокирован.")
            messages.success(request, f"Пользователь {user.email} разблокирован.")

        user.save()
        return redirect("users:users_list")


class CustomUserUpdateView(UpdateView):
    """
    Представление для обновления данных пользователя.
    """

    model = CustomUser
    form_class = CustomUserRegisterForm
    template_name = "users/profile.html"
    success_url = reverse_lazy("postpilot:welcome")

    def form_valid(self, form):
        """
        Переопределение метода для сохранения пользователя в базе данных.
        """
        self.object = form.save()  # Сохраняем объект формы в базу
        logger.info(f"Пользователь {self.object.email} успешно обновлен.")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Переопределение метода для обработки неверной формы обновления данных пользователя.
        """
        logger.error(f"Ошибка при обновлении данных пользователя: {form.errors}.")
        return super().form_invalid(form)


class CustomUserLogoutView(View):
    """
    Представление для выхода пользователя.
    """

    def get(self, request):
        """Обрабатывает GET-запрос для выхода пользователя."""
        logout(request)
        logger.info("Пользователь успешно вышел.")
        return redirect(reverse_lazy("postpilot:welcome"))

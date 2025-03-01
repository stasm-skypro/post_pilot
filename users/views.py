import logging

from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from users.forms import CustomUserRegisterForm
from users.models import CustomUser

logger = logging.getLogger(__name__)


class CustomUserRegisterView(CreateView):
    """
    Представление для регистрации нового пользователя.
    """

    model = CustomUser
    form_class = CustomUserRegisterForm
    template_name = "users/profile.html"
    success_url = reverse_lazy("postpilot:mailing_list")

    @staticmethod
    def send_welcome_email(user_email):
        """
        Отправляет сообщение на email пользователя при успешной регистрации..
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
        user = form.save()
        login(self.request, user)  # Автоматически аутентифицирует пользователя сразу после успешной регистрации
        logger.info("Пользователь {user.username} успешно зарегистрирован.")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Переопределение метода для обработки неверной формы регистрации.
        """
        logger.error("Ошибка при регистрации пользователя: {form.errors}.")
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
        logger.info(f"Пользователь {self.request.user.username} успешно авторизован.")
        return reverse_lazy("postpilot:mailing_list")


class CustomUserLogoutView(LogoutView):
    """
    Представление для выхода пользователя.
    """
    next_page = reverse_lazy("postpilot:mailing_list")  # Автоматическое перенаправление пользователя после выхода


class CustomUserUpdateView(UpdateView):
    """
    Представление для обновления данных пользователя.
    """
    model = CustomUser
    form_class = CustomUserRegisterForm
    template_name = "users/profile.html"
    success_url = reverse_lazy("postpilot:mailing_list")

    def form_valid(self, form):
        """
        Переопределение метода для сохранения пользователя в базе данных.
        """
        self.object = form.save()  # Сохраняем объект формы в базу
        logger.info(f"Пользователь {self.object.username} успешно обновлен.")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Переопределение метода для обработки неверной формы обновления данных пользователя.
        """
        logger.error("Ошибка при обновлении данных пользователя: {form.errors}.")
        return super().form_invalid(form)

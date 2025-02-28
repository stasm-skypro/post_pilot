from django.contrib.auth.models import AbstractUser
from django.db import models


# Создаём кастомную модель пользователя
class CustomUser(AbstractUser):
    """
    Класс пользователя. Модель 'Пользователь'.
    """

    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Имя пользователя",
        help_text="Введите имя пользователя",
        default="Johnny Depp",
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        help_text="Введите Email",
        default="johny.depp@ya.ru",
    )
    avatar = models.ImageField(
        upload_to="users/",
        verbose_name="Аватар",
        help_text="Загрузите аватар",
        default="/users/default_avatar.jpg",
        blank = True,
        null = True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [USERNAME_FIELD]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        """Переопределение метода __str__ для вывода имени пользователя."""
        return self.email

    def get_full_name(self):
        """Переопределение метода get_full_name для вывода полного имени пользователя."""
        return self.username

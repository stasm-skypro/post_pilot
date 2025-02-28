from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Класс менеджера пользователей. Нужен для правильного создания пользователей и суперпользователей в кастомной
    модели пользователя.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Метод для создания обычного пользователя.
        """
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, email, password=None, **extra_fields):
        """
        Метод для создания суперпользователя.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


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

    odjects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", ]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        """Переопределение метода __str__ для вывода имени пользователя."""
        return self.email

    def get_full_name(self):
        """Переопределение метода get_full_name для вывода полного имени пользователя."""
        return self.username

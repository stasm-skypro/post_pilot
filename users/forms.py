import logging
import os

from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator

from users.models import CustomUser

logger = logging.getLogger(__name__)

class CustomUserRegisterForm(UserCreationForm):
    """
    Класс формы регистрации пользователя.
    """

    class Meta:
        """
        Класс метаданных: валидация полей.
        """

        def clean_username(self):
            """
            Проверка, что username не содержит запрещённые слова.
            """
            username = self.cleaned_data.get("username")
            forbidden_words = os.getenv("FORBIDDEN_WORDS").split(",")
            for word in forbidden_words:
                if word in username.lower():
                    logger.warning(f"В поле 'Имя пользователя' использовано запрещенное слово '{word}'")
                    raise ValidationError(
                        f"В поле 'Имя пользователя' использовано запрещенное слово '{word}'"
                    )
            return username


        def clean_email(self):
            """
            Проверка, что указанные email не содержит запрещённые слова.
            """
            email = self.cleaned_data.get("email")

            #  Проверка, что указанные email не содержит запрещённые слова.
            forbidden_words = os.getenv("FORBIDDEN_WORDS").split(",")
            for word in forbidden_words:
                if word in email.lower():
                    logger.warning(f"В поле 'Email' использовано запрещенное слово '{word}'")
                    raise ValidationError(
                        f"В поле 'Email' использовано запрещенное слово '{word}'"
                    )
            return email


        def clean_email_format(self):
            """
            Проверка, что email имеет правильный формат.
            """
            email = self.cleaned_data.get("email")

            # Проверяем формат email с помощью EmailValidator
            email_validator = EmailValidator(message="Введите корректный email")
            try:
                email_validator(email)
            except ValidationError:
                logger.warning("Введите корректный email")
                raise ValidationError("Введите корректный email")

            return email

        def clean_email_unique(self):
            """
            Проверка, что email уникален. Уникальность проверяется для того, чтобы ошибка была показана на уровне формы
            до появления ошибки IntegrityError на уровне БД.
            """
            email = self.cleaned_data.get("email")

            if CustomUser.objects.filter(email=email).exists():
                logger.warning("Пользователь с таким email уже зарегистрирован")
                raise ValidationError("Пользователь с таким email уже зарегистрирован")
            
            return email


        def clean_image_size(self):
            """
            Проверка, что размер файла не превышает 2 мегабайта.
            """
            image = self.cleaned_data.get("image")
            if image and image.size > 2 * 1024 * 1024:
                logger.warning("Размер аватара не должен превышать 2 мегабайта")
                raise ValidationError("Размер аватара не должен превышать 2 мегабайта")
            return image


        def clean_image_format(self):
            """
            Проверка, что формат файла изображения - jpeg.
            """
            image = self.cleaned_data.get("image")
            if image and image.content_type != "image/jpeg" or image.content_type != "image/jpg" or image.content_type != "image/png":
                logger.warning("Формат файла изображения должен быть jpeg, jpg или png.")
                raise ValidationError("Формат файла изображения должен быть jpeg, jpg или png.")
            return image

import os

import logging
from django import forms

from .mixins import StyledFormMixin
from .models import Recipient, Message, Mailing, SendAttempt
from dotenv import load_dotenv

load_dotenv(override=True)

# Настройка логгера
logger = logging.getLogger("postpilot")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("postpilot/logs/reports.log", "a", "utf-8")
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
)
logger.addHandler(handler)


class RecipientForm(StyledFormMixin, forms.ModelForm):
    """Форма получателя рассылки."""

    class Meta:
        model = Recipient
        fields = "__all__"
        labels = {
            "email": "Email",
            "full_name": "ФИО",
            "comments": "Комментарии",
        }

    def clean_full_name(self):
        """Очищаем поле 'ФИО' от запрещенных слов."""

        forbidden_words = os.getenv("FORBIDDEN_WORDS").split(",")

        cleaned_data = super().clean()
        full_name = cleaned_data.get("full_name", "")
        for word in forbidden_words:
            if word in full_name.lower():
                logger.warning("В поле 'ФИО' запрещено использовать слово '%s'" % word)
                raise forms.ValidationError(
                    "В поле 'ФИО' запрещено использовать слово '%s'" % word
                )

        return full_name


def clean_email(self):
    forbidden_words = os.getenv("FORBIDDEN_WORDS").split(",")

    cleaned_data = super().clean()
    email = cleaned_data.get("email", "")
    for word in forbidden_words:
        if word in email.lower():
            logger.warning("В поле 'Email' запрещено использовать слово '%s'" % word)
            raise forms.ValidationError(
                "В поле 'Email' запрещено использовать слово '%s'" % word
            )
    return email


class MessageForm(StyledFormMixin, forms.ModelForm):
    """Форма сообщения рассылки."""

    class Meta:
        model = Message
        fields = "__all__"
        labels = {
            "subject": "Тема",
            "body_text": "Текст",
            "body_html": "HTML",
        }

    def clean_subject(self):
        forbidden_words = os.getenv("FORBIDDEN_WORDS").split(",")

        cleaned_data = super().clean()
        subject = cleaned_data.get("subject", "")
        for word in forbidden_words:
            if word in subject.lower():
                logger.warning("В поле 'Тема' запрещено использовать слово '%s'" % word)
                raise forms.ValidationError(
                    "В поле 'Тема' запрещено использовать слово '%s'" % word
                )
        return subject

    def clean_body_text(self):
        forbidden_words = os.getenv("FORBIDDEN_WORDS").split(",")

        cleaned_data = super().clean()
        body_text = cleaned_data.get("body_text", "")
        for word in forbidden_words:
            if word.lower() in body_text.lower():
                logger.warning(
                    "В поле 'Текст' запрещено использовать слово '%s'" % word
                )
                raise forms.ValidationError(
                    "В поле 'Текст' запрещено использовать слово '%s'" % word
                )
        return body_text


class MailingForm(StyledFormMixin, forms.ModelForm):
    """Форма рассылки."""

    class Meta:
        model = Mailing
        fields = "__all__"
        labels = {
            "first_sent_at": "Дата и время первой отправки",
            "sent_completed_at": "Дата и время окончания отправки",
            "status": "Статус",
            "message": "Сообщение",
            "recipients": "Получатели",
        }

    def clean_dates(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if start_date and end_date and start_date > end_date:
            logger.warning("Дата начала рассылки не может быть позже даты окончания")
            raise forms.ValidationError(
                "Дата начала рассылки не может быть позже даты окончания"
            )
        return cleaned_data

    # Здесь нет необходимости проверять на чистоту получателей и сообщений, так как они проверяются в соответствующих формах.


class SendAttemptForm(StyledFormMixin, forms.ModelForm):
    """
    Форма попытки отправки рассылки.
    """

    class Meta:
        model = SendAttempt
        fields = "__all__"
        labels = {
            "attempt_at": "Дата и время попытки",
            "status": "Статус",
            "response": "Ответ сервера",
            "mailing": "Рассылка",
        }

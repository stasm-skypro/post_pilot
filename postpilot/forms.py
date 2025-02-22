import os

from django import forms
from .models import Recipient, Message, Mailing
from dotenv import load_dotenv

load_dotenv(override=True)


class RecipientForm(forms.ModelForm):
    """Форма получателя рассылки."""

    class Meta:
        model = Recipient
        fields = '__all__'
        labels = {
            'email': 'Email',
            'full_name': 'ФИО',
            'comments': 'Комментарии',
        }

    def clean_full_name(self):
        """Очищаем поле 'ФИО' от запрещенных слов."""

        forbidden_words = os.getenv("FORBIDDEN_WORDS").split(',')

        cleaned_data = super().clean()
        full_name = cleaned_data['full_name']
        for word in forbidden_words:
            if word in full_name.lower():
                raise forms.ValidationError("В поле 'ФИО' запрещено использовать слово '%s'" % word)
        return cleaned_data


def clean_email(self):
    forbidden_words = os.getenv("FORBIDDEN_WORDS").split(',')

    cleaned_data = super().clean()
    email = cleaned_data['email']
    for word in forbidden_words:
        if word in email.lower():
            raise forms.ValidationError("В поле 'Email' запрещено использовать слово '%s'" % word)
    return cleaned_data


class MessageForm(forms.ModelForm):
    """Форма сообщения рассылки."""

    class Meta:
        model = Message
        fields = '__all__'
        labels = {
            'subject': 'Тема',
            'body_text': 'Текст',
            'body_html': 'HTML',
        }

    def clean_subject(self):
        forbidden_words = os.getenv("FORBIDDEN_WORDS").split(',')

        cleaned_data = super().clean()
        subject = cleaned_data['subject']
        for word in forbidden_words:
            if word in subject.lower():
                raise forms.ValidationError("В поле 'Тема' запрещено использовать слово '%s'" % word)
        return cleaned_data

    def clean_body_text(self):
        forbidden_words = os.getenv("FORBIDDEN_WORDS").split(',')

        cleaned_data = super().clean()
        body_text = cleaned_data['body_text']
        for word in forbidden_words:
            if word.lower() in body_text.lower():
                raise forms.ValidationError("В поле 'Текст' запрещено использовать слово '%s'" % word)
        return cleaned_data


class MailingForm(forms.ModelForm):
    """Форма рассылки."""

    class Meta:
        model = Mailing
        fields = '__all__'
        labels = {
            'first_sent_at': 'Дата и время первой отправки',
            'sent_completed_at': 'Дата и время окончания отправки',
            'status': 'Статус',
            'message': 'Сообщение',
            'recipients': 'Получатели',
        }

    def clean_dates(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Дата начала рассылки не может быть позже даты окончания")
        return cleaned_data

    # Нет необходимости проверять на чистоту получателей и сообщений, так как они проверяются в соответствующих формах.

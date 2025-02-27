from django.db import models


# -- Recipient model --
class Recipient(models.Model):
    """Класс получателя рассылки. Модель 'Получатель рассылки'."""

    email = models.EmailField("Email", unique=True)
    full_name = models.CharField("ФИО", max_length=255, blank=True, null=True)
    comments = models.TextField("Комментарии", blank=True)

    def __str__(self):
        """Возвращает строковое представление объекта 'Получатель рассылки'."""
        return f"{self.email} {self.full_name}"

    class Meta:
        """
        Класс метаданных 'Получатель рассылки'.
        """
        db_table = "recipients"
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"


# -- Message model --
class Message(models.Model):
    """Класс сообщения. Модель 'Сообщение'."""

    subject = models.CharField("Тема", max_length=100)
    body_text = models.TextField("Текст письма")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)  # Поле добавлено мной

    def __str__(self):
        """Возвращает строковое представление объекта 'Сообщение'."""
        return self.subject[:30]

    class Meta:
        """
        Класс метаданных 'Сообщение'.
        """
        db_table = "messages"
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["-created_at"]


# -- Mailing model --
class Mailing(models.Model):
    """Класс рассылки. Модель 'Рассылка'."""

    STATUS_CHOICES = [
        ("completed", "Завершено"),
        ("created", "Создано"),
        ("started", "Начато"),
        ("broken", "Прервано"),
    ]

    first_sent_at = models.DateTimeField("Дата первой отправки", blank=True, null=True)
    sent_completed_at = models.DateTimeField(
        "Дата завершения отправки", blank=True, null=True, auto_now=True
    )  # Используем auto_now=True в sent_completed_at, т.к. поле всегда обновляется при завершении
    status = models.CharField("Статус отправки", max_length=9, default="created", choices=STATUS_CHOICES)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name="Сообщение")
    recipients = models.ManyToManyField(Recipient, verbose_name="Получатели")

    def __str__(self):
        """Возвращает строковое представление объекта 'Рассылка'."""
        result = f"{self.message}"
        return result[:30]

    class Meta:
        """
        Класс метаданных 'Рассылка'.
        """
        db_table = "mailings"
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ["-sent_completed_at"]


# -- SendAttempt model --
class SendAttempt(models.Model):
    """Класс попытки рассылки. Модель 'Попытка рассылки'."""

    STATUS_CHOICES = [
        ("successfully", "Successfully"),
        ("failed", "Failed"),
    ]

    attempt_at = models.DateTimeField("Дата и время попытки отправки", auto_now_add=True)
    status = models.CharField("Статус отправки", max_length=12, choices=STATUS_CHOICES, default="failed")
    response = models.TextField("Ответ сервера", blank=True)
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, verbose_name="Рассылка")

    def __str__(self):
        """Возвращает строковое представление объекта 'Попытка рассылки'."""
        result = f"{self.response}"
        return result[:30]

    class Meta:
        """
        Класс метаданных 'Попытка рассылки'.
        """
        db_table = "send_attempts"
        verbose_name = "Попытка отправки"
        verbose_name_plural = "Попытки отправки"
        ordering = ["-attempt_at"]

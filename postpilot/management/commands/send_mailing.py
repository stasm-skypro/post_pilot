from django.core.mail import send_mail
from django.core.management.base import BaseCommand

from postpilot.models import Mailing


class Command(BaseCommand):
    """
    Кастомная команда отправки рассылки.
    """

    help = "Отправка всех активных рассылок"

    def handle(self, *args, **kwargs):
        """Обработчик команды."""
        mailings = Mailing.objects.filter(status="started")

        if not mailings.exists():
            self.stdout.write(self.style.WARNING("Нет активных рассылок."))
            return

        for mailing in mailings:
            recipients = mailing.recipients.all()
            recipient_list = [recipient.email for recipient in recipients]

            if recipient_list:
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.body_text,
                    from_email="no-reply@example.com",
                    recipient_list=recipient_list,
                )
                self.stdout.write(self.style.SUCCESS(f"Рассылка {mailing.id} успешно отправлена."))

        self.stdout.write(self.style.SUCCESS("Все активные рассылки отправлены."))

    def add_arguments(self, parser):
        """Позволяет отправить рассылку только для конкретного ID.
        Пример использования: ./manage.py send_mailing 3"""

        parser.add_argument("mailing_id", nargs="?", type=int, help="ID рассылки")

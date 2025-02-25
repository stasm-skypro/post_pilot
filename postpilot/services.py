"""
Сервис по отправке писем через SMTP.
"""

import logging

from django.conf import settings
from django.core.mail import send_mail

from .models import Mailing, Recipient, SendAttempt

logger = logging.getLogger("postpilot")


def send_mailing(mailing_id):
    """
    Отправляет письма всем получателям указанной рассылки.
    """
    try:
        mailing = Mailing.objects.get(id=mailing_id)
        recipients = Recipient.objects.all()
        subject = mailing.message.subject
        message = mailing.message.body_text
        from_email = settings.DEFAULT_FROM_EMAIL

        if not recipients.exists():
            logger.warning("Попытка отправки рассылки без получателей. ID рассылки: %s", mailing_id)
            return False

        recipient_list = [recipient.email for recipient in recipients]

        sent_count = send_mail(subject, message, from_email, recipient_list)

        # Записываем попытку отправки
        SendAttempt.objects.create(
            mailing=mailing,
            status="success" if sent_count > 0 else "failed",
            details=f"Отправлено {sent_count} писем.",
        )

        logger.info("Рассылка успешно отправлена. ID рассылки: %s, отправлено писем: %s", mailing_id, sent_count)
        return sent_count > 0

    except Mailing.DoesNotExist:
        logger.error("Рассылка с ID %s не найдена", mailing_id)
        return False
    except Exception as e:
        logger.error("Ошибка при отправке рассылки: %s", str(e))
        return False

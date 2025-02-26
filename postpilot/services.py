"""
Сервис по отправке писем через SMTP.
"""

import logging
import os

from django.core.mail import send_mail
from django.utils.timezone import now
from dotenv import load_dotenv

from .models import Mailing

# Настройка логгера
logger = logging.getLogger("postpilot")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("postpilot/logs/reports.log", "a", "utf-8")
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s"))
logger.addHandler(handler)


load_dotenv(override=True)


def send_mailing(mailing: Mailing):
    """
    Отправляет письма всем получателям указанной рассылки.
    Обновляет статус рассылки на "started" перед отправкой и "completed" после завершения.
    """
    print("mailing", mailing.__dict__)
    mailing.status = "started"
    mailing.first_sent_at = now()
    mailing.save(update_fields=["status", "first_sent_at"])
    print("mailing", mailing.__dict__)

    recipients = mailing.recipients.all()
    recipient_list = [recipient.email for recipient in recipients]
    print("recipient_list", recipient_list)

    if not recipient_list:
        logger.warning(f"Рассылка {mailing.id} не имеет получателей!")
        return

    try:
        send_mail(
            subject=mailing.message.subject,
            message=mailing.message.body_text,
            from_email=os.getenv("EMAIL_HOST_USER"),
            recipient_list=recipient_list,
            fail_silently=False,  # Если ошибка, Django вызовет исключение
        )

        mailing.status = "completed"
        mailing.sent_completed_at = now()
        mailing.save(update_fields=["status", "sent_completed_at"])
        logger.info("Рассылка %s успешно отправлена." % mailing.id)

    except Exception as e:
        mailing.status = "broken"  # Переводим в состояние "broken connection"
        mailing.save(update_fields=["status"])
        logger.error("Ошибка при отправке рассылки %s: %s" % (mailing.id, e))
        raise

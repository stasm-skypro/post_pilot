"""
Сервис по отправке писем через SMTP.
"""

import logging
import os

from django.core.mail import send_mail
from django.utils.timezone import now
from dotenv import load_dotenv

from postpilot.models import Mailing, SendAttempt

logger = logging.getLogger(__name__)

load_dotenv()


# def send_mailing(mailing: Mailing):
#     """
#     Отправляет письма всем получателям указанной рассылки.
#     Обновляет статус рассылки и фиксирует попытки отправки.
#     Чтобы от сервера SMTP получить индивидуальные ответы для каждого получателя, используется smtplib
#     """
#
#     # Переводим статус рассылки в состояние 'started'
#     mailing.status = "started"
#     mailing.first_sent_at = now()
#     mailing.save(update_fields=["status", "first_sent_at"])
#
#     # Генерим список получателей
#     recipients = mailing.recipients.all()
#     recipient_list = [recipient.email for recipient in recipients]
#
#     # Если список получателей пуст, то пишем предупреждение в лог и в БД
#     if not recipient_list:
#         logger.warning(f"Рассылка {mailing.id} не имеет получателей!")
#         SendAttempt.objects.create(
#             mailing=mailing,
#             status="failed",
#             response="Рассылка не имеет получателей.",
#         )
#         return
#
#     # Настройки SMTP
#     smtp_host = os.getenv("EMAIL_HOST")
#     smtp_port = int(os.getenv("EMAIL_PORT", 587))
#     smtp_user = os.getenv("EMAIL_HOST_USER")
#     smtp_password = os.getenv("EMAIL_HOST_PASSWORD")
#
#     try:
#         # Используем контекстный менеджер для автоматического закрытия соединения
#         with smtplib.SMTP(smtp_host, smtp_port) as server:
#             server.connect(smtp_host, smtp_port)
#             server.starttls()
#             server.login(smtp_user, smtp_password)
#
#             responses = []
#
#             # Для каждого получателя из списка:
#             for recipient in recipient_list:
#                 try:
#                     # Формируем письмо
#                     msg = MIMEMultipart()
#                     msg["Subject"] = mailing.message.subject
#                     msg["From"] = smtp_user
#                     msg["To"] = recipient  # ОДИН получатель в письме
#                     msg.attach(MIMEText(mailing.message.body_text, "plain"))
#
#                     response = server.sendmail(smtp_user, recipient, msg.as_string())
#
#                     # Если `response` пустой, значит, письмо отправлено успешно
#                     if not response:
#                         response_text = "Успешно отправлено"
#                         status = "successfully"
#                     else:
#                         response_text = f"Ошибка отправки: {response}"
#                         status = "failed"
#
#                 # Если ошибка соединения или отправки
#                 except smtplib.SMTPException as e:
#                     response_text = f"Ошибка SMTP: {str(e)}"
#                     status = "failed"
#
#                 # Логируем и сохраняем попытку отправки
#                 logger.info(f"Письмо на {recipient}: {response_text}")
#                 SendAttempt.objects.create(
#                     mailing=mailing,
#                     status=status,
#                     response=f"{recipient}: {response_text}",
#                 )
#
#                 responses.append(f"{recipient}: {response_text}")
#
#         # Если сервер отработал без исключений, помечаем рассылку как завершённую
#         mailing.status = "completed"
#         mailing.sent_completed_at = now()
#         logger.info(f"Рассылка {mailing.id} завершена.")
#
#     # Если сервер упал, логируем и записываем ошибку в БД
#     except Exception as e:
#         mailing.status = "broken"
#         # logger.debug(f"Ошибка при отправке рассылки {mailing.id}: {e}")
#         logger.exception(f"Ошибка при отправке рассылки {mailing.id}: {e}")
#
#         SendAttempt.objects.create(
#             mailing=mailing,
#             status="failed",
#             response=f"Общая ошибка: {e}",
#         )
#
#     # Если всё норм, обновляем статус и время окончания рассылки
#     finally:
#         mailing.save(update_fields=["status", "sent_completed_at"])


def send_mailing(mailing: Mailing):
    """
    Отправляет письма всем получателям указанной рассылки.
    Использует django.core.mail.send_mail для отправки.
    Обновляет статус рассылки и фиксирует попытки отправки.
    """

    # Переводим статус рассылки в состояние 'started'
    mailing.status = "started"
    mailing.first_sent_at = now()
    mailing.save(update_fields=["status", "first_sent_at"])

    # Генерируем список получателей
    recipients = mailing.recipients.all()
    recipient_list = [recipient.email for recipient in recipients]

    # Если список получателей пуст, фиксируем это в БД и логах
    if not recipient_list:
        logger.warning(f"Рассылка {mailing.id} не имеет получателей!")
        SendAttempt.objects.create(
            mailing=mailing,
            status="broken",  # Прерываем рассылку, так как отправлять некуда
            response="Рассылка не имеет получателей.",
        )
        mailing.status = "broken"
        mailing.save(update_fields=["status"])
        return

    try:
        # Отправка писем
        sent_count = send_mail(
            subject=mailing.message.subject,
            message=mailing.message.body_text,
            from_email=os.getenv("EMAIL_HOST_USER"),
            recipient_list=recipient_list,
            fail_silently=False,  # Ошибки не игнорируем (не уверен, что так надо)
        )

        # Если хотя бы одно письмо отправлено успешно
        if sent_count > 0:
            status = "completed"
            response_text = f"Отправлено {sent_count} писем"
        else:
            status = "broken"  # Если не отправлено ни одного письма, это считается прерыванием
            response_text = "Не удалось отправить письма"

        # Логируем и сохраняем попытку отправки
        logger.info(f"Рассылка {mailing.id}: {response_text}")
        SendAttempt.objects.create(
            mailing=mailing,
            status=status,
            response=response_text,
        )

        # Обновляем статус рассылки
        mailing.status = status

    except Exception as e:
        # Логируем и записываем ошибку в БД
        mailing.status = "broken"
        logger.exception(f"Ошибка при отправке рассылки {mailing.id}: {e}")

        SendAttempt.objects.create(
            mailing=mailing,
            status="broken",
            response=f"Ошибка отправки: {e}",
        )

    finally:
        mailing.save(update_fields=["status", "sent_completed_at"])

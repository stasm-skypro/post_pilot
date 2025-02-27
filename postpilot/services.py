"""
Сервис по отправке писем через SMTP.
"""

import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.utils.timezone import now
from dotenv import load_dotenv

from postpilot.models import Mailing, SendAttempt

logger = logging.getLogger(__name__)

load_dotenv(override=True)


# def send_mailing(mailing: Mailing):
#     """
#     Отправляет письма всем получателям указанной рассылки.
#     Обновляет статус рассылки и фиксирует попытки отправки.
#     """
#     # Вариант 1
#     # TODO: Нужно чтобы логировался в БД ответ smtp-сервера по каждому получателю
#
#     mailing.status = "started"
#     mailing.first_sent_at = now()
#     mailing.save(update_fields=["status", "first_sent_at"])
#
#     recipients = mailing.recipients.all()
#     recipient_list = [recipient.email for recipient in recipients]
#     # recipient_list = list(mailing.recipients.values_list("email", flat=True))
#
#     if not recipient_list:
#         logger.warning(f"Рассылка {mailing.id} не имеет получателей!")
#         SendAttempt.objects.create(
#             mailing=mailing,
#             status="failed",
#             response="Рассылка не имеет получателей.",
#         )
#         return
#
#     try:
#         send_mail(
#             subject=mailing.message.subject,
#             message=mailing.message.body_text,
#             from_email=os.getenv("EMAIL_HOST_USER"),
#             recipient_list=recipient_list,
#             fail_silently=True,  # Чтобы ошибки не прерывали всю отправку
#         )
#
#         mailing.status = "completed"
#         mailing.sent_completed_at = now()
#
#         logger.info(f"Рассылка {mailing.id} успешно отправлена.")
#
#         # Записываем успешную попытку в БД
#         SendAttempt.objects.create(
#             mailing=mailing,
#             status="successfully",
#             response="Рассылка успешно отправлена.",
#         )
#
#     except Exception as e:
#         mailing.status = "broken"  # Переводим в состояние "broken connection"
#         logger.exception(f"Ошибка при отправке рассылки {mailing.id}: {e}")
#
#         # Записываем неудачную попытку в БД
#         SendAttempt.objects.create(
#             mailing=mailing,
#             status="failed",
#             response=str(e),
#         )
#
#     finally:
#         mailing.save(update_fields=["status", "sent_completed_at"])


# def send_mailing(mailing: Mailing):
#     """
#     Отправляет письма всем получателям указанной рассылки.
#     Обновляет статус рассылки и фиксирует попытки отправки.
#     Чтобы от сервера SMTP получить индивидуальные ответы для каждого получателя, используется smtplib.
#     """
#
#     # Вариант 2
#     # TODO: Чтобы исключить ошибку 'please run connect() first' прикрутим with smtplib.SMTP()
#
#     mailing.status = "started"
#     mailing.first_sent_at = now()
#     mailing.save(update_fields=["status", "first_sent_at"])
#
#     recipients = mailing.recipients.all()
#     recipient_list = [recipient.email for recipient in recipients]
#
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
#     server = None  # Переменная для сервера SMTP
#
#     try:
#         # Подключаемся к серверу
#         server = smtplib.SMTP(smtp_host, smtp_port)
#         server.starttls()
#         server.login(smtp_user, smtp_password)
#
#         # Формируем письмо
#         msg = MIMEMultipart()
#         msg["Subject"] = mailing.message.subject
#         msg["From"] = smtp_user
#         msg.attach(MIMEText(mailing.message.body_text, "plain"))
#
#         responses = []
#
#         for recipient in recipient_list:
#             try:
#                 msg["To"] = recipient
#                 response = server.sendmail(smtp_user, recipient, msg.as_string())
#
#                 # Если нет ошибок, считаем отправку успешной
#                 if not response:
#                     response_text = "Успешно отправлено"
#                     status = "successfully"
#                 else:
#                     response_text = f"Ошибка отправки: {response}"
#                     status = "failed"
#
#             except smtplib.SMTPException as e:
#                 response_text = f"Ошибка SMTP: {str(e)}"
#                 status = "failed"
#
#             # Логируем и сохраняем попытку отправки для каждого получателя
#             logger.info(f"Письмо на {recipient}: {response_text}")
#             # Записываем попытку в БД
#             SendAttempt.objects.create(
#                 mailing=mailing,
#                 status=status,
#                 response=f"{recipient}: {response_text}",
#             )
#
#             responses.append(f"{recipient}: {response_text}")
#
#         server.quit()
#
#         # Успешное завершение рассылки, обновляем статус рассылки
#         mailing.status = "completed"
#         mailing.sent_completed_at = now()
#         logger.info(f"Рассылка {mailing.id} завершена.")
#
#     except Exception as e:
#         mailing.status = "broken"
#         # logger.exception(f"Ошибка при отправке рассылки {mailing.id}: {e}")
#         logger.debug(f"Ошибка при отправке рассылки {mailing.id}: {e}")
#
#         # Записываем ошибку в БД
#         SendAttempt.objects.create(
#             mailing=mailing,
#             status="failed",
#             response=f"Общая ошибка: {e}",
#         )
#
#     finally:
#         if server:
#             try:
#                 server.noop()  # Проверка, живо ли соединение
#                 server.quit()
#             except smtplib.SMTPServerDisconnected:
#                 logger.warning("Соединение с SMTP-сервером уже закрыто.")
#
#         mailing.save(update_fields=["status", "sent_completed_at"])


def send_mailing(mailing: Mailing):
    """
    Отправляет письма всем получателям указанной рассылки.
    Обновляет статус рассылки и фиксирует попытки отправки.
    Чтобы от сервера SMTP получить индивидуальные ответы для каждого получателя, используется smtplib
    """

    # Переводим статус рассылки в состояние 'started'
    mailing.status = "started"
    mailing.first_sent_at = now()
    mailing.save(update_fields=["status", "first_sent_at"])

    # Генерим список получателей
    recipients = mailing.recipients.all()
    recipient_list = [recipient.email for recipient in recipients]

    # Если список получателей пуст, то пишем предупреждение в лог и в БД
    if not recipient_list:
        logger.warning(f"Рассылка {mailing.id} не имеет получателей!")
        SendAttempt.objects.create(
            mailing=mailing,
            status="failed",
            response="Рассылка не имеет получателей.",
        )
        return

    # Настройки SMTP
    smtp_host = os.getenv("EMAIL_HOST")
    smtp_port = int(os.getenv("EMAIL_PORT", 587))
    smtp_user = os.getenv("EMAIL_HOST_USER")
    smtp_password = os.getenv("EMAIL_HOST_PASSWORD")

    try:
        # Используем контекстный менеджер для автоматического закрытия соединения
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)

            responses = []

            # Для каждого получателя из списка:
            for recipient in recipient_list:
                try:
                    # Формируем письмо
                    msg = MIMEMultipart()
                    msg["Subject"] = mailing.message.subject
                    msg["From"] = smtp_user
                    msg["To"] = recipient  # ОДИН получатель в письме
                    msg.attach(MIMEText(mailing.message.body_text, "plain"))

                    response = server.sendmail(smtp_user, recipient, msg.as_string())

                    # Если `response` пустой, значит, письмо отправлено успешно
                    if not response:
                        response_text = "Успешно отправлено"
                        status = "successfully"
                    else:
                        response_text = f"Ошибка отправки: {response}"
                        status = "failed"

                # Если ошибка соединения или отправки
                except smtplib.SMTPException as e:
                    response_text = f"Ошибка SMTP: {str(e)}"
                    status = "failed"

                # Логируем и сохраняем попытку отправки
                logger.info(f"Письмо на {recipient}: {response_text}")
                SendAttempt.objects.create(
                    mailing=mailing,
                    status=status,
                    response=f"{recipient}: {response_text}",
                )

                responses.append(f"{recipient}: {response_text}")

        # Если сервер отработал без исключений, помечаем рассылку как завершённую
        mailing.status = "completed"
        mailing.sent_completed_at = now()
        logger.info(f"Рассылка {mailing.id} завершена.")

    # Если сервер упал, логируем и записываем ошибку в БД
    except Exception as e:
        mailing.status = "broken"
        # logger.debug(f"Ошибка при отправке рассылки {mailing.id}: {e}")
        logger.exception(f"Ошибка при отправке рассылки {mailing.id}: {e}")

        SendAttempt.objects.create(
            mailing=mailing,
            status="failed",
            response=f"Общая ошибка: {e}",
        )

    # Если всё норм, обновляем статус и время окончания рассылки
    finally:
        mailing.save(update_fields=["status", "sent_completed_at"])

    # Как-то так...

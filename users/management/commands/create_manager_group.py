from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from postpilot.models import Mailing, Recipient, Message, SendAttempt
from users.models import CustomUser


class Command(BaseCommand):
    """
    Кастомная команда для создания группы Менеджеры.
    Создает группу Менеджеры с нужными правами.
    Менеджеры обладают правами:
    1. Просмотр всех клиентов и рассылок, сообщений и попыток рассылок.
    2. Просмотр списка пользователей сервиса.
    3. Блокировка пользователей сервиса.
    4. Отключение рассылок.
    """

    help = "Создает группу Менеджеры с нужными правами"

    def handle(self, *args, **kwargs):
        """
        Обработчик команды.
        """
        managers_group, created = Group.objects.get_or_create(name="Менеджеры")

        # Модели, к которым нужен доступ
        models = [Mailing, Recipient, Message, SendAttempt, CustomUser]

        # Список прав
        perms = ["view", "change"]  # Просмотр и изменение

        # Добавляем права к группе
        for model in models:
            content_type = ContentType.objects.get_for_model(model)
            for perm in perms:
                permission = Permission.objects.filter(
                    codename=f"{perm}_{model._meta.model_name}", content_type=content_type
                ).first()
                if permission:
                    managers_group.permissions.add(permission)

        self.stdout.write(self.style.SUCCESS("Группа 'Менеджеры' успешно создана!"))

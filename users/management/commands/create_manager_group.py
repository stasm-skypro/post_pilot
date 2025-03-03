from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from postpilot.models import Mailing, Recipient, Message, SendAttempt
from users.models import CustomUser


class Command(BaseCommand):
    help = "Создает группу Менеджеры с нужными правами"

    def handle(self, *args, **kwargs):
        managers_group, created = Group.objects.get_or_create(name="Менеджеры")

        models = [Mailing, Recipient, Message, SendAttempt, CustomUser]
        perms = ["view", "change"]  # Права просмотра и редактирования

        for model in models:
            content_type = ContentType.objects.get_for_model(model)
            for perm in perms:
                permission = Permission.objects.get(codename=f"{perm}_{model._meta.model_name}", content_type=content_type)
                managers_group.permissions.add(permission)

        self.stdout.write(self.style.SUCCESS("Группа 'Менеджеры' успешно создана!"))

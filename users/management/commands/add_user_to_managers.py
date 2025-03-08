from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from users.models import CustomUser


class Command(BaseCommand):
    """
    Кастомная команда для добавления пользователя в группу 'Менеджеры'.
    """

    help = "Добавляет пользователя в группу 'Менеджеры'"

    def add_arguments(self, parser):
        """Добавляет аргументы команды."""
        parser.add_argument("email", type=str, help="Email пользователя")

    def handle(self, *args, **options):
        """Обработчик команды."""
        email = options["email"]
        try:
            user = CustomUser.objects.get(email=email)
            managers_group, created = Group.objects.get_or_create(name="Менеджеры")
            user.groups.add(managers_group)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Пользователь {email} добавлен в группу 'Менеджеры'."))
        except CustomUser.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Пользователь {email} не найден."))

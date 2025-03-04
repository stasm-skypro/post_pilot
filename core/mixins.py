from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class StyledFormMixin:
    """Миксин для стилизации формы."""

    def __init__(self, *args, **kwargs):
        """Осуществляет стилизацию формы."""

        super().__init__(*args, **kwargs)

        for _, field in self.fields.items():
            if isinstance(field, forms.BooleanField):
                field.widget.attrs.update(
                    {
                        "class": "form-check-input",
                    }
                )
            else:
                field.widget.attrs.update(
                    {
                        "class": "form-control",
                        "placeholder": field.label,
                        "style": "font-size: 0.9em; width: 100%",
                    }
                )


class OwnerRequiredMixin(LoginRequiredMixin):
    """
    Миксин для проверки владения объектом. Ограничивает доступ так, чтобы пользователь мог управлять только своими
    объектами.
    """

    owner_field = "owner"  # Поле модели, содержащее владельца

    def get_queryset(self):
        """Возвращает только объекты, принадлежащие текущему пользователю."""
        query_set = super().get_queryset()
        return query_set.filter(**{self.owner_field: self.request.user})

    def form_valid(self, form):
        """Дополнительная обработка перед сохранением формы. При создании объекта автоматически проставляет владельца."""
        if not form.instance.pk:  # Проверяем, создается ли объект
            setattr(form.instance, self.owner_field, self.request.user)   # Устанавливаем текущего пользователя владельцем
        return super().form_valid(form)


class MenegerRequiredMixin(UserPassesTestMixin):
    """
    Позволяет менеджерам видеть все объекты, но запрещает изменять или удалять чужие данные.
    """

    def test_func(self):
        """Проверяет, является ли пользователь владельцем объекта или менеджером.
        Менеджеры могут только просматривать, а владельцы могут редактировать."""

        obj = self.get_object()
        user = self.request.user

        if user.is_superuser:  # Суперпользователи имеют полный доступ
            return True

        if user.groups.filter(name="Менеджеры").exists():  # Проверяем, является ли пользователь менеджером
            # Менеджеры могут только просматривать
            return self.request.method in ["GET", "HEAD", "OPTIONS"]

        # Обычные пользователи могут работать только со своими данными
        return getattr(obj, "owner", None) == user

    def handle_no_permission(self):
        """Вызывает ошибку 403, если у пользователя нет доступа."""
        raise PermissionDenied("У вас нет прав для выполнения этого действия.")


class IsManagerOrOwnerListMixin(UserPassesTestMixin):
    """
    Ограничивает доступ:
    - Владельцам (видят только свои объекты).
    - Менеджерам (видят все, но не могут редактировать).
    Миксин написан специально для контроллеров, использующих базовый класс ListView, который не имеет метода
    get_object.
    """

    def test_func(self):
        user = self.request.user

        # Менеджеры могут просматривать список
        if user.groups.filter(name="Менеджеры").exists():
            return True

        # Владельцы могут видеть только свои объекты
        return user.is_authenticated

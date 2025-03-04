from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.cache import cache


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
        query_set = cache.get("query_set")

        if not query_set:
            query_set = super().get_queryset()
            cache.set("query_set", query_set, 60 * 15)  # 15 минут кэширования
        return query_set.filter(**{self.owner_field: self.request.user})

    def form_valid(self, form):
        """Дополнительная обработка перед сохранением формы. При создании объекта автоматически проставляет владельца."""
        if not form.instance.pk:  # Проверяем, создается ли объект
            setattr(
                form.instance, self.owner_field, self.request.user
            )  # Устанавливаем текущего пользователя владельцем
        return super().form_valid(form)


class IsManagerOrOwnerListMixin(UserPassesTestMixin):
    """
    Ограничивает доступ:
    - Владельцам (видят только свои объекты).
    - Менеджерам (видят все, но не могут редактировать).
    """

    owner_field = "owner"  # Поле модели, содержащее владельца

    def test_func(self):
        """Разрешает доступ менеджерам и владельцам."""
        user = self.request.user
        return user.groups.filter(name="Менеджеры").exists() or user.is_authenticated

    def get_queryset(self):
        """Ограничивает видимость объектов по владельцу."""
        user = self.request.user

        query_set = super().get_queryset()

        if user.groups.filter(name="Менеджеры").exists():
            return query_set  # Менеджеры видят все

        return query_set.filter(**{self.owner_field: user})  # Владельцы видят только свои

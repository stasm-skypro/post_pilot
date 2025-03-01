from django import forms


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

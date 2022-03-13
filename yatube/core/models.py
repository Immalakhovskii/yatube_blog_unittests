from django.db import models


class ModelWithDateAndText(models.Model):
    text = models.TextField(
        "Текст",
        help_text="Введите текст",
    )
    created = models.DateTimeField(
        "Дата создания",
        auto_now_add=True,
    )

    class Meta:
        abstract = True

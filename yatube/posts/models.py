from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

CHARS_OF_POST_TEXT = 15


class Group(models.Model):
    title = models.CharField("Название группы", max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        "Текст поста",
        help_text="Введите текст поста"
    )
    pub_date = models.DateTimeField(
        "Дата публикации",
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор"
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="posts",
        verbose_name="Группа",
        help_text="Выберите группу",
    )

    def __str__(self):
        return self.text[:CHARS_OF_POST_TEXT]

    class Meta:
        ordering = ["-pub_date"]

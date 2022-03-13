from django.contrib.auth import get_user_model
from django.db import models
from core.models import ModelWithDateAndText

User = get_user_model()

CHARS_OF_POST_TEXT = 15
CHARS_OF_COMMENT_TEXT = 15


class Group(models.Model):
    title = models.CharField("Название группы", max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(ModelWithDateAndText):
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

    image = models.ImageField(
        "Картинка",
        upload_to="posts/",
        blank=True
    )

    def __str__(self):
        return self.text[:CHARS_OF_POST_TEXT]

    class Meta:
        ordering = ["-created"]
        verbose_name = "Пост"
        verbose_name_plural = "Посты"


class Comment(ModelWithDateAndText):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Пост",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор",
    )

    def __str__(self):
        return self.text[:CHARS_OF_COMMENT_TEXT]

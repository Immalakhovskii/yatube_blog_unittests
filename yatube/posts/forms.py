from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group")  # "image"
        labels = {
            "text": _("Текст поста"),
            "group": _("Группа"),
        }
        help_texts = {
            "text": _("Введите текст поста"),
            "group": _("Выберите группу"),
        }

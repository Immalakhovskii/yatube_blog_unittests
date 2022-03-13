from faker import Faker

from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()

CHARS_OF_POST_TEXT = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        fake = Faker()
        cls.user = User.objects.create_user(
            username=fake.name()
        )
        cls.group = Group.objects.create(
            title=fake.word(),
        )
        cls.post = Post.objects.create(
            author=cls.user,
        )

    def test_models_have_correct_objects_names(self):
        """Проверка корректной работы __str__ в моделях."""
        group = PostModelTest.group
        post = PostModelTest.post
        objects_names = (
            (str(group), group.title),
            (str(post), post.text[:CHARS_OF_POST_TEXT]),
        )
        for title, expected_title in objects_names:
            with self.subTest(title=title):
                self.assertEqual(title, expected_title)

    def test_post_model_verbose_names(self):
        """Проверка verbose_name в полях."""
        post = PostModelTest.post
        field_verboses = {
            "text": "Текст",
            "created": "Дата создания",
            "author": "Автор",
            "group": "Группа",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_post_model_help_texts(self):
        """Проверка совпадения help_texts в полях с ожидаемыми."""
        post = PostModelTest.post
        field_help_texts = {
            "text": "Введите текст",
            "group": "Выберите группу",
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value
                )

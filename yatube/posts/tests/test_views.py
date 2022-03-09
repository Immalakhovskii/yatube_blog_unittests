from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms
from faker import Faker

from ..models import Post, Group

User = get_user_model()


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        fake = Faker()
        cls.user = User.objects.create_user(
            username=fake.name(),
        )
        cls.group = Group.objects.create(
            title=fake.word(),
            slug=fake.slug(),
        )
        cls.group2 = Group.objects.create(
            id=fake.random_int(),
        )
        cls.post = Post.objects.create(
            id=fake.random_int(),
            author=cls.user,
            group=cls.group,
            text=fake.text(),
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_group_and_profile_show_correct_context(self):
        """Проверка контекста шаблонов index, group_posts и profile"""
        responses = [
            (self.guest_client.get(reverse("posts:index"))),
            (self.guest_client.get(reverse("posts:group_list",
             kwargs={"slug": self.group.slug}))),
            (self.guest_client.get(reverse("posts:profile",
             kwargs={"username": self.user.username}))),
        ]
        for response in responses:
            first_object = response.context["posts"][0]
            first_object_attributes = {
                first_object.author.username: self.user.username,
                first_object.text: self.post.text,
                first_object.group.title: self.group.title,
            }
            for instance, expected_instance in first_object_attributes.items():
                with self.subTest(instance=instance):
                    self.assertEqual(instance, expected_instance)

    def test_post_detail_shows_correct_context(self):
        """Проверка контекста шаблона post_detail"""
        response = (self.guest_client.get(reverse("posts:post_detail",
                    kwargs={"post_id": self.post.id})))
        first_object = response.context["post"]
        first_object_attributes = {
            first_object.author.username: self.user.username,
            first_object.text: self.post.text,
            first_object.group.title: self.group.title,
        }
        for instance, expected_instance in first_object_attributes.items():
            with self.subTest(instance=instance):
                self.assertEqual(instance, expected_instance)

    def test_post_create_and_post_edit_show_correct_context(self):
        """Проверка контекста шаблонов post_create и post_edit."""
        responses = [
            (self.authorized_client.get(reverse("posts:post_create"))),
            (self.authorized_client.get(reverse("posts:post_edit",
             kwargs={"post_id": self.post.id}))),
        ]
        for response in responses:
            form_fields = {
                "text": forms.fields.CharField,
                "group": forms.models.ModelChoiceField,
            }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get("form").fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_post_with_group_belongs_only_to_its_group(self):
        """Проверка принадлежности поста только своей группе."""
        response = self.guest_client.get(reverse("posts:group_list",
                                         kwargs={"slug": self.group.slug}))
        self.assertNotEqual(response.context.get("group").id,
                            self.group2.id)

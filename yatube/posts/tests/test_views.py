from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from ..models import Post, Group
from ..views import POSTS_PER_PAGE

User = get_user_model()

POSTS_FOR_TESTS = 13


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_group",
        )
        cls.group2 = Group.objects.create(
            title="Тестовая группа 2",
            slug="test_group2"
        )
        cls.post = Post.objects.create(
            id=1,
            author=cls.user,
            group=cls.group,
            text="Вполне себе длинный тестовый пост",
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_use_correct_templates(self):
        """Проверка использования правильных шаблонов в URL-адресах."""
        page_names_templates = {
            reverse("posts:index"): "posts/index.html",
            reverse("posts:post_create"): "posts/create_post.html",
            reverse("posts:group_list", kwargs={"slug": "test_group"}): (
                "posts/group_list.html"
            ),
            reverse("posts:profile", kwargs={"username": "auth"}): (
                "posts/profile.html"
            ),
            reverse("posts:post_detail", kwargs={"post_id": 1}): (
                "posts/post_detail.html"
            ),
            reverse("posts:post_edit", kwargs={"post_id": 1}): (
                "posts/create_post.html"
            )
        }
        for reverse_name, template in page_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_group_and_profile_show_correct_context(self):
        """Проверка контекста шаблонов index, group_posts и profile"""
        responses = [
            (self.guest_client.get(reverse("posts:index"))),
            (self.guest_client.get(reverse("posts:group_list",
             kwargs={"slug": "test_group"}))),
            (self.guest_client.get(reverse("posts:profile",
             kwargs={"username": "auth"}))),
        ]
        for response in responses:
            first_object = response.context["posts"][0]
            first_object_attributes = {
                first_object.author.username: "auth",
                first_object.text: "Вполне себе длинный тестовый пост",
                first_object.group.title: "Тестовая группа",
            }
            for instance, expected_instance in first_object_attributes.items():
                with self.subTest(instance=instance):
                    self.assertEqual(instance, expected_instance)

    def test_post_with_group_belongs_only_to_its_group(self):
        """Проверка принадлежности поста только своей группе."""
        response = self.guest_client.get(reverse("posts:group_list",
                                         kwargs={"slug": "test_group"}))
        self.assertNotEqual(response.context.get("group").id,
                            self.group2.id)

    def test_post_detail_shows_correct_context(self):
        """Проверка контекста шаблона post_detail"""
        response = (self.guest_client.get(reverse("posts:post_detail",
                    kwargs={"post_id": 1})))
        first_object = response.context["post"]
        first_object_attributes = {
            first_object.author.username: "auth",
            first_object.text: "Вполне себе длинный тестовый пост",
            first_object.group.title: "Тестовая группа",
        }
        for instance, expected_instance in first_object_attributes.items():
            with self.subTest(instance=instance):
                self.assertEqual(instance, expected_instance)

    def test_post_create_and_post_edit_show_correct_context(self):
        """Проверка контекста шаблонов post_create и post_edit."""
        responses = [
            (self.authorized_client.get(reverse("posts:post_create"))),
            (self.authorized_client.get(reverse("posts:post_edit",
             kwargs={"post_id": 1}))),
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


class PaginatorPostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_group",
        )
        for i in range(0, (POSTS_FOR_TESTS)):
            cls.post = Post.objects.create(author=cls.user,
                                           group=cls.group)

    def setUp(self):
        self.guest_client = Client()

    def test_first_pages_have_expected_number_of_records(self):
        """Проверка ожидаемого числа объектов на первых страницах
        index, group_list и profile."""
        page_with_objects = {
            reverse("posts:index"): POSTS_PER_PAGE,
            reverse("posts:group_list", kwargs={"slug": "test_group"}):
            POSTS_PER_PAGE,
            reverse("posts:profile", kwargs={"username": "auth"}):
            POSTS_PER_PAGE,
        }
        for page, objects in page_with_objects.items():
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(len(response.context["page_obj"]), objects)

    def test_second_pages_have_expected_number_of_records(self):
        """Проверка ожидаемого числа объектов на вторых страницах
        index, group_list и profile."""
        posts_count = POSTS_FOR_TESTS - POSTS_PER_PAGE
        page_with_objects = {
            reverse("posts:index"): posts_count,
            reverse("posts:group_list", kwargs={"slug": "test_group"}):
            posts_count,
            reverse("posts:profile", kwargs={"username": "auth"}): posts_count,
        }
        for page, objects in page_with_objects.items():
            with self.subTest(page=page):
                response = self.guest_client.get(page + "?page=2")
                self.assertEqual(len(response.context["page_obj"]), objects)

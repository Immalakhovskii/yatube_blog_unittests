from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group
from ..forms import PostForm

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            slug="test_group",
        )
        cls.post = Post.objects.create(
            id=1,
            author=cls.user,
            group=cls.group,
            text="Вполне себе длинный тестовый пост",
        )
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_creation_is_possible(self):
        """Валидная форма создает запись в Post"""
        posts_count = Post.objects.count()
        form_data = {
            "text": "Вполне себе длинный тестовый пост",
            "group": self.group.id,
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse("posts:profile",
                              kwargs={"username": self.user.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text="Вполне себе длинный тестовый пост",
                group=self.group.id,
            ).exists()
        )

    def test_post_editing_is_possible(self):
        """Валидная форма изменяет запись в Post"""
        posts_count = Post.objects.count()
        form_data = {
            "text": "Вполне себе длинный тестовый пост с правками",
        }
        response = self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse("posts:post_detail",
                              kwargs={"post_id": self.post.id}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text="Вполне себе длинный тестовый пост с правками",
            ).exists()
        )

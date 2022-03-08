from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from faker import Faker

from ..models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_group",
        )
        cls.post = Post.objects.create(
            id=1,
            author=cls.user,
            text="Вполне себе длинный тестовый пост",
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_public_posts_urls_exist_at_desired_location(self):
        """Проверка доступных для анонима URL posts."""
        url_status = {
            "/": HTTPStatus.OK,
            "/group/test_group/": HTTPStatus.OK,
            "/profile/auth/": HTTPStatus.OK,
            "/posts/1/": HTTPStatus.OK,
        }
        for url, status in url_status.items():
            with self.subTest(status=status):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_posts_create_and_edit_urls_exist_at_desired_location(self):
        """Проверка доступных URL posts для авторизованных пользователей."""
        url_status = {
            "/create/": HTTPStatus.OK,
            "/posts/1/edit/": HTTPStatus.OK,
        }
        for url, status in url_status.items():
            with self.subTest(status=status):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_nonexistent_url_drops_404(self):
        """Проверка запроса к несущетвующему URL."""
        fake = Faker()
        response = self.guest_client.get(f"/{fake.url()}/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_create_and_edit_redirect_anonymous(self):
        """Проверка редиректов анонима с create/ и posts/edit/."""
        response = self.guest_client.get("/create/", follow=True)
        self.assertRedirects(response, "/auth/login/?next=/create/")
        response = self.guest_client.get("/posts/1/edit/", follow=True)
        self.assertRedirects(response, "/auth/login/?next=/posts/1/edit/")

    def test_posts_urls_use_correct_template(self):
        """Проверка использования правильных шаблонов в URL-адресах."""
        urls_for_templates = {
            "/": "posts/index.html",
            "/group/test_group/": "posts/group_list.html",
            "/profile/auth/": "posts/profile.html",
            "/posts/1/": "posts/post_detail.html",
            "/create/": "posts/create_post.html",
            "/posts/1/edit/": "posts/create_post.html",
        }
        for address, template in urls_for_templates.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

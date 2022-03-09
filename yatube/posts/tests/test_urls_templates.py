from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from faker import Faker

from ..models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        fake = Faker()
        cls.user = User.objects.create_user(
            username=fake.name()
        )
        cls.group = Group.objects.create(
            slug=fake.slug(),
        )
        cls.post = Post.objects.create(
            id=fake.random_int(),
            author=cls.user,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_posts_urls_use_correct_template(self):
        """Проверка использования правильных шаблонов в URL-адресах."""
        urls_for_templates = {
            "/": "posts/index.html",
            f"/group/{self.group.slug}/": "posts/group_list.html",
            f"/profile/{self.user.username}/": "posts/profile.html",
            f"/posts/{self.post.id}/": "posts/post_detail.html",
            "/create/": "posts/create_post.html",
            f"/posts/{self.post.id}/edit/": "posts/create_post.html",
        }
        for address, template in urls_for_templates.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
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

    def test_pages_use_correct_templates(self):
        """Проверка использования правильных шаблонов в URL-адресах."""
        page_names_templates = {
            reverse("posts:index"): "posts/index.html",
            reverse("posts:post_create"): "posts/create_post.html",
            reverse("posts:group_list", kwargs={"slug": self.group.slug}):
            ("posts/group_list.html"),
            reverse("posts:profile", kwargs={"username": self.user.username}):
            ("posts/profile.html"),
            reverse("posts:post_detail", kwargs={"post_id": self.post.id}):
            ("posts/post_detail.html"),
            reverse("posts:post_edit", kwargs={"post_id": self.post.id}):
            ("posts/create_post.html"),
        }
        for reverse_name, template in page_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

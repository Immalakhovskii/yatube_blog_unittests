from faker import Faker

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group, Comment

User = get_user_model()

FIRST_OBJECT = 0


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        fake = Faker()
        cls.user = User.objects.create_user(
            username=fake.name(),
        )
        cls.group = Group.objects.create(
            id=fake.random_int(),
            slug=fake.slug(),
        )
        cls.group2 = Group.objects.create(
            id=fake.random_int(),
        )
        cls.post = Post.objects.create(
            id=fake.random_int(),
            author=cls.user,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
        )

    def setUp(self):
        self.guest_client = Client()

    def test_post_with_group_belongs_only_to_its_group(self):
        """Проверка принадлежности поста только своей группе."""
        response = self.guest_client.get(reverse("posts:group_list",
                                         kwargs={"slug": self.group.slug}))
        self.assertNotEqual(response.context.get("group").id,
                            self.group2.id)

    def test_post_detail_has_related_comment(self):
        """Проверка наличия комментария поста на странице post_detail."""
        response = self.guest_client.get(reverse("posts:post_detail",
                                         kwargs={"post_id": self.post.id}))
        comment = response.context.get("comments")[FIRST_OBJECT]
        self.assertEqual(comment, self.comment)

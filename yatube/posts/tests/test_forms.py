from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from faker import Faker

from ..models import Post, Group
from ..forms import PostForm

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        fake = Faker()
        cls.user = User.objects.create_user(
            username=fake.name(),
        )
        cls.another_user = User.objects.create_user(
            username=fake.name(),
        )
        cls.group = Group.objects.create(
            slug=fake.slug(),
        )
        cls.post = Post.objects.create(
            id=fake.random_int(),
            author=cls.user,
            group=cls.group,
            text=fake.text(),
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.another_authorized_client = Client()
        self.another_authorized_client.force_login(self.another_user)

    def test_post_creation_is_possible(self):
        """Проверка создания записи в Post авторизованным пользователем."""
        posts_count = Post.objects.count()
        form_data = {
            "text": self.post.text,
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
                id=self.post.id,
                text=form_data["text"],
                group=self.group.id,
            ).exists()
        )

    def test_post_editing_is_possible(self):
        """Проверка редактирования объекта Post автором."""
        posts_count = Post.objects.count()
        edited_text = Faker()
        form_data = {
            "text": edited_text.text(),
            "group": self.group.id,
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
                text=form_data["text"],
                group=self.group.id,
            ).exists()
        )

    def test_anonym_cant_create_post(self):
        """Проверяем, что аноним не может сделать запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            "text": self.post.text,
            "group": self.group.id,
        }
        response = self.guest_client.post(
            reverse("posts:post_create"),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, "/auth/login/?next=/create/")
        self.assertEqual(Post.objects.count(), posts_count)

    def test_anonym_cant_edit_post(self):
        """Проверяем, что аноним не может редактировать Post."""
        posts_count = Post.objects.count()
        edited_text = Faker()
        form_data = {
            "text": edited_text.text(),
            "group": self.group.id,
        }
        response = self.guest_client.post(
            reverse("posts:post_edit", kwargs={"post_id": self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            f"/auth/login/?next=/posts/{self.post.id}/edit/"
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFalse(
            Post.objects.filter(
                text=form_data["text"],
                group=self.group.id,
            ).exists()
        )

    def test_not_author_cant_edit_post(self):
        """Проверяем, что авторизованный пользователь не может
        редактировать не свой Post."""
        posts_count = Post.objects.count()
        edited_text = Faker()
        form_data = {
            "text": edited_text.text(),
            "group": self.group.id,
        }
        response = self.another_authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("posts:post_detail",
                    kwargs={"post_id": self.post.id}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFalse(
            Post.objects.filter(
                text=form_data["text"],
                group=self.group.id,
            ).exists()
        )

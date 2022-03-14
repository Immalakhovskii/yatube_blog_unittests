import shutil
import tempfile
from faker import Faker

from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from ..models import Post, Group
from ..forms import PostForm

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.another_authorized_client = Client()
        self.another_authorized_client.force_login(self.another_user)

    def test_post_creation_is_possible(self):
        """Проверка создания объекта Post авторизованным пользователем."""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name="small.gif",
            content=small_gif,
            content_type="image/gif"
        )
        posts_count = Post.objects.count()
        form_data = {
            "text": self.post.text,
            "group": self.group.id,
            "image": uploaded,
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
                author=self.user,
                text=form_data["text"],
                group=self.group.id,
                image="posts/small.gif",
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

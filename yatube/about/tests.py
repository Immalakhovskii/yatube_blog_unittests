from django.test import TestCase, Client
from http import HTTPStatus


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_exist_at_desired_location(self):
        """Проверка URL about."""
        url_status = {
            "/about/author/": HTTPStatus.OK,
            "/about/tech/": HTTPStatus.OK,
        }
        for url, status in url_status.items():
            with self.subTest(status=status):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_posts_urls_use_correct_template(self):
        """Проверка шаблонов about."""
        templates_url_names = {
            "about/author.html": "/about/author/",
            "about/tech.html": "/about/tech/",
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

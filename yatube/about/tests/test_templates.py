from django.test import TestCase, Client


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

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

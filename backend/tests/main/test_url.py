from django.test import TestCase
from django.urls import reverse

class FrontendRoutingTest(TestCase):

    def test_get_csrf_token_url(self):
        response = self.client.get(reverse('get_csrf_token'))
        self.assertEqual(response.status_code, 200)

    def test_random_route(self):
        response = self.client.get('/some-random-route/')
        self.assertTemplateUsed(response, 'index.html')
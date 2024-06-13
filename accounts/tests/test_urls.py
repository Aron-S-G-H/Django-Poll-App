from django.test import SimpleTestCase
from accounts import views
from django.urls import reverse, resolve


class AccountTestUrl(SimpleTestCase):

    def test_login(self):
        url = reverse('accounts:login')
        self.assertEqual(resolve(url).func.view_class, views.Login)

    def test_register(self):
        url = reverse('accounts:register')
        self.assertEqual(resolve(url).func.view_class, views.Register)

    def test_logout(self):
        url = reverse('accounts:logout')
        self.assertEqual(resolve(url).func, views.user_logout)

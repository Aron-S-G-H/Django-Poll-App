from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.forms import LoginForm, RegisterForm


class TestUserLoginView(TestCase):
    def setUp(self):
        User.objects.create_user(username='example', email='example@example.com', password='example1234')
        self.client = Client()

    def test_user_login_GET_notAuthenticated(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.failUnless(response.context['form'], LoginForm)

    def test_user_login_GET_authenticated(self):
        self.client.login(username='example', email='example@example.com', password='example1234')
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_user_login_POST_valid(self):
        response = self.client.post(reverse('accounts:login'), data={'username': 'example', 'password': 'example1234'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('polls:list'))

    def test_user_login_POST_invalid(self):
        response = self.client.post(reverse('accounts:login'), data={'username': 'root', 'password': 'example1234'})
        self.failIf(response.context['form'].is_valid())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.failUnless(response.context['form'], LoginForm)
        self.assertFormError(form=response.context['form'], field='username', errors=['Invalid User Data'])


class TestUserRegisterView(TestCase):
    def setUp(self):
        User.objects.create_user(username='example', email='example@example.com', password='example1234')
        self.client = Client()

    def test_user_register_GET_notAuthenticated(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
        self.failUnless(response.context['form'], RegisterForm)

    def test_user_register_GET_authenticated(self):
        self.client.login(username='example', email='example@example.com', password='example1234')
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_user_register_POST_valid(self):
        register_form_data = {
            'username': 'root',
            'email': 'root@example.com',
            'password1': 'root1234',
            'password2': 'root1234',
        }
        form = RegisterForm(register_form_data)
        self.assertTrue(form.is_valid())
        response = self.client.post(reverse('accounts:register'), data=register_form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('polls:list'))
        self.assertEqual(User.objects.count(), 2)

    def test_user_register_POST_invalid(self):
        register_form_data = {
            'username': 'root',
            'email': 'root@example.com',
            'password1': 'root1234',
            'password2': 'root12345',
        }
        register_form_data2 = {
            'username': 'example',
            'email': 'example@example.com',
            'password1': 'example1234',
            'password2': 'example1234',
        }
        form = RegisterForm(register_form_data)
        self.failIf(form.is_valid())
        response = self.client.post(reverse('accounts:register'), data=register_form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
        self.failUnless(response.context['form'], RegisterForm)
        self.assertFormError(form=response.context['form'], field='password1', errors=['Passwords are not the same !!'])
        self.assertEqual(User.objects.count(), 1)
        form = RegisterForm(register_form_data2)
        response2 = self.client.post(reverse('accounts:register'), data=register_form_data2)
        self.assertTrue(form.is_valid())
        self.failUnless(response2.context['form'], RegisterForm)
        self.assertTemplateUsed(response2, 'accounts/register.html')
        self.assertFormError(form=response2.context['form'], field='username', errors=['Username or Email already exists!'])
        self.assertEqual(User.objects.count(), 1)


"""Tests of the sign up view."""
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from ..Log_in_helper import LogInTester
from ...forms import SignUpForm
from ...models import User
from ...models import MembershipType
class SignUpViewTestCase(TestCase, LogInTester):
    """Tests of the sign up view."""

    def setUp(self):
        self.url = reverse('sign_up')
        self.form_input = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'janedoe@example.org',
            'public_bio': 'My bio',
            'personal_statement': 'Hi there !',
            'chess_experience_level': '1',
            'new_password': 'Password123',
            'password_confirmation': 'Password123'
        }

    def test_sign_up_url(self):
        """ Test case to check if the redirected url is equivalent to the
            expected url for signing up """
        self.assertEqual(self.url,'/sign_up/')

    def test_get_sign_up(self):
        """ Test case to check if the sign up form is in bound and is an instance
            of the SignUpForm """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertFalse(form.is_bound)

    def test_unsuccesful_sign_up(self):
        """ Test case for unsuccssfull sign up when an invalid email address
            is entered """
        self.form_input['email'] = 'badMail'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self._is_logged_in())

    def test_succesful_sign_up(self):
        """ Test case for succssfull sign up when all fields entered satisifed
            the requirments """
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('user_profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        user = User.objects.get(email='janedoe@example.org')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'janedoe@example.org')
        self.assertEqual(user.personal_statement, 'Hi there !')
        self.assertEqual(user.public_bio, 'My bio')
        self.assertEqual(user.chess_experience_level, 1)
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)
        self.assertTrue(self._is_logged_in())

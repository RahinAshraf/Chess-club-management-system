"""Unit tests of the sign up form."""
from django.contrib.auth.hashers import check_password
from django import forms
from django.test import TestCase
from ...forms import SignUpForm
from ...models import MembershipType, User
from ...Constants import consts
class SignUpFormTestCase(TestCase):
    """Unit tests of the sign up form."""

    def setUp(self):
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

    def test_valid_sign_up_form(self):
        form = SignUpForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = SignUpForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('public_bio', form.fields)
        self.assertIn('personal_statement', form.fields)
        self.assertIn('chess_experience_level', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))
        self.assertIn('new_password', form.fields)
        new_password_widget = form.fields['new_password'].widget
        self.assertTrue(isinstance(new_password_widget, forms.PasswordInput))
        self.assertIn('password_confirmation', form.fields)
        password_confirmation_widget = form.fields['password_confirmation'].widget

    def test_new_password_and_password_confirmation_are_identical(self):
        self.form_input['password_confirmation'] = 'WrongPassword123'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = SignUpForm(data=self.form_input)
        before_membership_type_count = MembershipType.objects.count()
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        after_membership_type_count = MembershipType.objects.count()
        self.assertEqual(after_count, before_count+1)
        self.assertEqual(after_membership_type_count, before_membership_type_count + 1)
        # check membership type credentials
        user = User.objects.get(email='janedoe@example.org')
        membership_type = MembershipType.objects.filter(user = user)[0].type
        self.assertEqual(membership_type, consts.APPLICANT)
        # check user credentials
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'janedoe@example.org')
        self.assertEqual(user.personal_statement, 'Hi there !')
        self.assertEqual(user.public_bio, 'My bio')
        self.assertEqual(user.chess_experience_level, 1)
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)

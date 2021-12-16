from django.test import TestCase
from clubs.models import User
from django.core.exceptions import ValidationError


class UserModelTestCase(TestCase):
    """ Unit tests of the user models """

    fixtures = ['clubs/Tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(first_name = "John")

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except (ValidationError) :
            self.fail('Test User should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def test_valid_user(self):
        self._assert_user_is_valid()

    def test_email_must_be_unique(self):
        new_user = User.objects.create_user(
            first_name = 'Test',
            last_name = 'Case',
            email = 'testCaseNew@example.com',
            password = 'Password123',
            public_bio = 'Hello!!',
            chess_experience_level = 3,
            personal_statement = 'I want to play chess!!'
        )

        self.user.email = 'testCaseNew@example.com'

        self._assert_user_is_invalid()

    def test_maximum_length_of_first_name(self):
        self.user.first_name = 's' * 51
        self._assert_user_is_invalid()

    def test_maximum_length_of_last_name(self):
        self.user.last_name = 's' * 51
        self._assert_user_is_invalid()

    def test_maximum_length_of_public_bio(self):
        self.user.public_bio = 's' * 521
        self._assert_user_is_invalid()

    def test_first_name_cannot_be_blank(self):
        self.user.first_name = ''
        self._assert_user_is_invalid()

    def test_last_name_cannot_be_blank(self):
        self.user.last_name = ''
        self._assert_user_is_invalid()

    def test_personal_statement_cannot_be_blank(self):
        self.user.personal_statement = ''
        self._assert_user_is_invalid()

    def test_first_name_may_already_exist(self):
        new_user = User.objects.create_user(
            first_name = 'Tes',
            last_name = 'Case',
            email = 'testCaseNew@example.com',
            password = 'Password123',
            public_bio = 'Hello!!',
            chess_experience_level = 3,
            personal_statement = 'I want to play chess!!'
        )

        self.user.first_name = 'Tes'
        self._assert_user_is_valid()

    def test_last_name_may_already_exist(self):
        new_user = User.objects.create_user(
            first_name = 'Test',
            last_name = 'Cas',
            email = 'testCaseNew@example.com',
            password = 'Password123',
            public_bio = 'Hello!!',
            chess_experience_level = 3,
            personal_statement = 'I want to play chess!!'
        )

        self.user.last_name = 'Cas'
        self._assert_user_is_valid()

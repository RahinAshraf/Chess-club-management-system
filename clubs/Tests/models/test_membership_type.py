from django.test import TestCase
from clubs.models import User
from clubs.models import MembershipType
from django.core.exceptions import ValidationError
from django.db import IntegrityError
class MembershipModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
                    first_name = 'Test',
                    last_name = 'Case',
                    email = 'testCase@example.com',
                    password = 'Password123',
                    public_bio = 'Hello!!',
                    chess_experience_level = 3,
                    personal_statement = 'I want to play chess!!')
        self.membership_type = MembershipType.objects.create(user = self.user, type = "applicant")
        
    def _assert_memberhip_type_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.membership_type.full_clean()

    def _assert_membership_type_is_valid(self):
        try:
            self.user.full_clean()
        except (ValidationError) :
            self.fail('Test User should be valid')

    def test_valid_membership_type(self):
        self._assert_membership_type_is_valid()

    def test_type_cannot_be_empty(self):
        self.membership_type.type = ''
        self._assert_memberhip_type_is_invalid()
    
    def test_user_cannot_hold_multiple_types(self):
        with self.assertRaises(IntegrityError):
            new_membership = MembershipType.objects.create(user = self.user, type = "applicant")

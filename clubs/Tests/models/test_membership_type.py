import copy
from django.test import TestCase
from clubs.models import Club, User
from clubs.models import MembershipType
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from ...Constants import consts
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
        
        self.club = Club.objects.create(club_owner = self.user,name = "Club1", location = 'location1', 
                                        mission_statement = 'We want to allow all to play free chess')
        

        self.membership_type = MembershipType.objects.get(user = self.user, club = self.club ,type = consts.CLUB_OWNER)
        
    def _assert_memberhip_type_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.membership_type.full_clean()

    def test_valid_membership_type(self):
        # This creation of another user and membership type is done because the self.user changes concurrently and validation can be a challenge
        user2 = User.objects.create_user(
                    first_name = 'Test',
                    last_name = 'Case',
                    email = 'testCaseNew@example.com',
                    password = 'Password123',
                    public_bio = 'Hello!!',
                    chess_experience_level = 3,
                    personal_statement = 'I want to play chess!!')
        membership_type2 = MembershipType.objects.create(user = user2, club = self.club, type = consts.MEMBER)
        try:
            membership_type2.full_clean()
        except (ValidationError) :
            self.fail('Test membership type should be valid')

    def test_type_cannot_be_empty(self):
        self.membership_type.type = ''
        self._assert_memberhip_type_is_invalid()
    
    def test_user_cannot_hold_multiple_types(self):
        """ This just tests that a user cannot hold multiple memberships simulatneously """
        with self.assertRaises(ValueError):
            new_membership = MembershipType.objects.create(user = self.user, club = self.club , type = consts.MEMBER)

    def test_invalid_membership_types(self):
        self.membership_type.type = 'Bad type'
        with self.assertRaises(ValidationError):
            self.membership_type.full_clean()

    def test_invalid_creation_of_two_club_owners(self):
        new_user = User.objects.create_user(
                    first_name = 'Test',
                    last_name = 'Case',
                    email = 'testCase2@example.com',
                    password = 'Password123',
                    public_bio = 'Hello!!',
                    chess_experience_level = 3,
                    personal_statement = 'I want to play chess!!')
        with self.assertRaises(ValueError):
            new_user_membership_type = self.membership_type = MembershipType.objects.create(user = new_user, club = self.club,type = consts.CLUB_OWNER)


    def test_invalid_change_to_club_owner(self):
        """ This tests whether a user who is initially not a club owner is wrongly changed to a club owner when one already exists. """
        new_user = User.objects.create_user(
                    first_name = 'Test',
                    last_name = 'Case',
                    email = 'testCase2@example.com',
                    password = 'Password123',
                    public_bio = 'Hello!!',
                    chess_experience_level = 3,
                    personal_statement = 'I want to play chess!!')
        new_user_membership_type = self.membership_type = MembershipType.objects.create(user = new_user, club = self.club, type = consts.APPLICANT)
        
        # changing the new membership type to club owner when one already exists
        new_user_membership_type.type = consts.CLUB_OWNER
        with self.assertRaises(ValidationError):
            new_user_membership_type.full_clean()

    def test_user_can_be_a_member_of_many_clubs(self):
        try:
            club3 = Club.objects.create(club_owner = self.user,name = "Club3", location = 'location1', 
                                        mission_statement = 'We want to allow all to play free chess')
        except :
            self.fail('Test membership type should be valid')
        
        try:
            club4 = Club.objects.create(club_owner = self.user,name = "Club4", location = 'location1', 
                                    mission_statement = 'We want to allow all to play free chess')
        except :
            self.fail('Test membership type should be valid')
 

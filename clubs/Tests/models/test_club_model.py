from django.db.utils import IntegrityError
from django.test import TestCase
from clubs.models import Club, User
from django.core.exceptions import ValidationError


class MembershipModelTestCase(TestCase):
 
                  
    def setUp(self):
        self.user = User.objects.create_user(
                    first_name = 'Test',
                    last_name = 'Case',
                    email = 'testCase2@example.com',
                    password = 'Password123',
                    public_bio = 'Hello!!',
                    chess_experience_level = 3,
                    personal_statement = 'I want to play chess!!')
        self.club = Club.objects.create(club_owner = self.user,name = "Club1", location = 'location1', 
                                        mission_statement = 'We want to allow all to play free chess')
    
    def _assert_club_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.club.full_clean()

    def test_name_should_be_unique(self):        
        with self.assertRaises(IntegrityError):
            Club.objects.create(name = "Club1", location = 'location1', 
                        mission_statement = 'We want to allow all to play free chess')

    def test_location_should_not_be_blank(self):
        self.club.location = ''
        self._assert_club_is_invalid()
    
    def test_mission_statement_should_not_be_blank(self):
        self.club.mission_statement = ''
        self._assert_club_is_invalid()    

        
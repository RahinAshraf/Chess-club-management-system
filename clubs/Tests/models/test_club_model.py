from django.db.utils import IntegrityError
from django.test import TestCase
from clubs.models import Club
from django.core.exceptions import ValidationError

class MembershipModelTestCase(TestCase):

    def setUp(self):
        self.club = Club.objects.create(name = "Club1", location = 'location1', 
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

        
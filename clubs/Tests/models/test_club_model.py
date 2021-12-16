from django.db.utils import IntegrityError
from django.test import TestCase
from clubs.models import Club, MembershipType, User
from django.core.exceptions import ValidationError

class ClubModelTestCase(TestCase):
    """ Unit tests of the club models"""

    fixtures = ['clubs/Tests/fixtures/default_user.json','clubs/Tests/fixtures/default_set_up_of_clubs_and_tournament_with_owners_and_officers.json']

    def setUp(self):
        self.user = User.objects.get(first_name = "Russell")
        self.club = Club.objects.get(pk = 'Kerbal Chess Club')
        self.membershipType = MembershipType.objects.create(user = self.user, club = self.club, type = 'club_owner')

    def _assert_club_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.club.full_clean()

    def test_name_should_be_unique(self):
        with self.assertRaises(IntegrityError):
            Club.objects.create(club_owner = self.user, name = "Kerbal Chess Club", location = 'location1',
                        mission_statement = 'We want to allow all to play free chess')

    def test_location_should_not_be_blank(self):
        self.club.location = ''
        self._assert_club_is_invalid()

    def test_mission_statement_should_not_be_blank(self):
        self.club.mission_statement = ''
        self._assert_club_is_invalid()

    def test_get_all_users(self):
        user = self.club.get_all_users()
        self.assertEqual(user[0], self.user) # Using [0] because the test has only one user for now

    def test_club_has_right_owner(self):
        self.assertEqual(self.user, self.membershipType.user)

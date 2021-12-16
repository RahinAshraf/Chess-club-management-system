from django.test import TestCase
from clubs.models import Club, User, MembershipType, Match
from django.core.exceptions import ValidationError
from ...Constants import consts
class TestCaseForMatchModel(TestCase):
    fixtures = ['clubs/Tests/fixtures/default_user.json','clubs/Tests/fixtures/default_set_up_of_clubs_and_tournament_with_owners_and_officers.json']
    def setUp(self):
        self.user = User.objects.get(first_name = "Russell")
        self.user2 = User.objects.get(first_name = 'John')
        self.club = Club.objects.get(pk = 'Kerbal Chess Club')

        self.match = Match.objects.create(date = '2021-12-17', player1 = self.user, player2 = self.user2)


    def test_valid_match(self):
        try:
            self.match.full_clean()
        except (ValidationError) :
            self.fail('Test match should be valid')

    def _assert_invalid_match(self):
       with self.assertRaises(ValidationError):
           self.match.save()

    def test_a_match_cannot_be_within_the_same_player(self):
        """This tests whether a match can correctly reject inputs where the both players are pointing
        to the same user."""
        self.match.player2 = self.user
        self._assert_invalid_match()
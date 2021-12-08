from django.test import TestCase
from clubs.models import Club, User, MembershipType, Match
from django.core.exceptions import ValidationError
from ...Constants import consts
class TestCaseForMatchModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
                    first_name = 'Test',
                    last_name = 'Case',
                    email = 'testCase@example.com',
                    password = 'Password123',
                    public_bio = 'Hello!!',
                    chess_experience_level = 3,
                    personal_statement = 'I want to play chess!!')

        self.user2 = User.objects.create_user(
                    first_name = 'Test',
                    last_name = 'Case',
                    email = 'testCase2@example.com',
                    password = 'Password123',
                    public_bio = 'Hello!!',
                    chess_experience_level = 3,
                    personal_statement = 'I want to play chess!!')
        self.club = Club.objects.create(club_owner = self.user,name = "Club1.0", location = 'location1', 
                                        mission_statement = 'We want to allow all to play free chess')

        self.membership2 = MembershipType.objects.create(user = self.user2, club = self.club, type = consts.OFFICER)

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
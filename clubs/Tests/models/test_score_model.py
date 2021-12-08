from django.test import TestCase
from clubs.models import User, Score, Match
from django.core.exceptions import ValidationError
from ...Constants import consts

class ScoreModelTestCase(TestCase):
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

        self.match = Match.objects.create(date = '2021-12-17', player1 = self.user, player2 = self.user2)

        self.score = Score.objects.create(player = self.user, match = self.match, score = 1)

        self.score2 = Score.objects.create(player = self.user2, match = self.match, score = 0)


    def _assert_valid_tounrment(self):
        try:
            self.score.full_clean()
            self.score2.full_clean()
        except (ValidationError) :
            self.fail('Test tournament should be valid')

    def test_valid_scores(self):
        self._assert_valid_tounrment()

    def test_invalid_score(self):
        with self.assertRaises(ValidationError):
            self.score.score = 23 # Putting an invalid score.
            self.score.full_clean()
        
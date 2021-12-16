from django.test import TestCase
from clubs.models import Club, Round, User, MembershipType, Tournament, Match
from django.core.exceptions import ValidationError
from ...Constants import consts

class RoundModelTestCase(TestCase):
    """ Unit tests of the round models """

    fixtures = ['clubs/Tests/fixtures/default_user.json','clubs/Tests/fixtures/default_set_up_of_clubs_and_tournament_with_owners_and_officers.json']

    def setUp(self):
        self.user = User.objects.get(first_name = "Russell")
        self.user2 = User.objects.get(first_name = 'John')
        self.club = Club.objects.get(pk = 'Kerbal Chess Club')
        self.Tournament = Tournament.objects.get(pk = 1)

        self.officer = User.objects.create_user(
                    first_name = 'Test',
                    last_name = 'Case',
                    email = 'testCaseOfficer@example.com',
                    password = 'Password123',
                    public_bio = 'Hello!!',
                    chess_experience_level = 3,
                    personal_statement = 'I want to play chess!!')

        self.membership = MembershipType.objects.create(user = self.officer, club = self.club, type = consts.OFFICER)
        self.membership2 = MembershipType.objects.create(user = self.user2, club = self.club, type = consts.OFFICER)

        self.round=Round(Tournament=self.Tournament)
        self.round.save()

    def test_match_is_made(self):
        self._create_test_users()
        self.round.createMatches()
        self.assertEquals(self.round.matches.count(),5)

    def test_get_all_matches(self):
        self._create_test_users()
        self.round.createMatches()
        matches_in_this_round = self.round.get_all_matches()
        self.assertEquals(len(matches_in_this_round),5)

    def test_remove_losers_from_tournament(self):
        self._create_test_users()
        winner = []
        winner.append(self.round.players.all()[0])
        self.round.remove_losers_from_tournament_participant_list(winner)
        self.assertEqual(self.round.Tournament.participating_players.all().count(),1)
        self.assertEqual(self.round.Tournament.participating_players.all()[0],winner[0])

    def add_players(self):
        self.round.players.add(self.user)
        self.round.players.add(self.user2)

    def _create_test_users(self, user_count=10):
        """This method creates users and adds them to the round."""
        for user_id in range(user_count):
            user = User.objects.create_user(email=f'user{user_id}@test.org',
                password='Password123',
                first_name=f'First{user_id}',
                last_name=f'Last{user_id}',
                public_bio=f'Bio {user_id}',
                chess_experience_level='1',
                personal_statement=f'personal_statement{user_id}',
                )
            MembershipType.objects.create(user = user, club = self.club, type = consts.MEMBER)
            self.round.players.add(user)
            self.Tournament.participating_players.add(user)

    def _create_test_match_results(self):
        for match in self.round.matches.all():
            match.put_score_for_player(round = self.round, score = 1,player=match.player1)
            match.put_score_for_player2(round = self.round, score = 0)

    def test_winners_are_decided_accordingly(self):
        self._create_test_users()
        self.round.createMatches()
        self._create_test_match_results()
        self.round.decideWinners()
        self.assertEqual(self.round.Tournament.participating_players.all().count(),5)

    def test_winners_are_not_decided_if_all_matches_have_not_occurred(self):
        self._create_test_users()
        self.round.createMatches()
        match = self.round.matches.all()[0]
        match.put_score_for_player(round = self.round, score = 1,player=match.player1)
        match.put_score_for_player(round = self.round, score = 0,player=match.player2)
        self.round.decideWinners()
        self.assertEqual(self.round.Tournament.participating_players.all().count(),10)

    def test_decide_winners_for_zero_matches(self):
        self._create_test_users()
        self.round.decideWinners()
        self.assertEqual(self.round.Tournament.participating_players.all().count(),10)
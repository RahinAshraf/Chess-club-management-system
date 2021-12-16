from django.test import TestCase
from clubs.models import Club, Group, Round, User, MembershipType, Tournament
from django.core.exceptions import ValidationError
from django.urls import reverse
from ...Constants import consts
from django.contrib import messages

class ScorePlayerTestCase(TestCase):
    """Test case for Scoring player."""
    fixtures = ['clubs/Tests/fixtures/default_user.json','clubs/Tests/fixtures/default_set_up_of_clubs_and_tournament_with_owners_and_officers.json']
    
    def setUp(self):
        self.user = User.objects.get(first_name = 'Russell')
        self.officer = User.objects.get(first_name = 'Valentina')
        self.club = Club.objects.get(pk='Kerbal Chess Club')
        MembershipType.objects.create(user=self.user,club=self.club,type=consts.CLUB_OWNER)
        self.membership = MembershipType.objects.create(user = self.officer, club = self.club, type = consts.OFFICER)
        self.tournament = Tournament.objects.get(pk=1)

    def score_matches_in_round(self,round):
        for match in round.matches.all():
            response_url = reverse("score_player", kwargs={"round_id":round.pk,"match_id":match.pk,"player_id":match.player1.pk})
            self.client.get(response_url, follow=True)

    def _assert_match_creation_in_round(self,number_of_matches,number_of_players):
        """This method generates the matches and tests the number of players in the round and the number of matches"""
        response_url = reverse("generate_matches", kwargs={"tournament_id":self.tournament.pk})
        response = self.client.post(response_url, follow=True)
        round = Round.objects.get(Tournament = self.tournament)
        self.assertEqual(round.players.all().count(),number_of_players)
        self.assertEqual(round.matches.all().count(),number_of_matches)


    def test_score_matches_for_10_players(self):
        self._create_test_users()
        self.client.login(email=self.officer.email, password='Password123')
        self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        self._assert_match_creation_in_round(5,10)
        round = Round.objects.get(Tournament = self.tournament)
        self.score_matches_in_round(round)
        self._assert_match_creation_in_round(2,4)

    def test_test_score_matches_for_17_players(self):
        self._create_test_users(user_count=17)
        self.client.login(email=self.officer.email, password='Password123')
        self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        self._assert_match_creation_in_group(6,4)
        groups = Group.objects.filter(Tournament = self.tournament)
        self.assertEqual(len(groups),4)
        for group in groups:
            self.score_matches_in_round(group)
        self.assertEqual(self.tournament.participating_players.all().count(),9)

    def _assert_match_creation_in_group(self,number_of_matches,number_of_groups):
        """This method generates the matches and tests the number of groups created and the number of matches in each group"""
        response_url = reverse("generate_matches", kwargs={"tournament_id":self.tournament.pk})
        response = self.client.post(response_url, follow=True)
        groups = Group.objects.filter(Tournament = self.tournament)
        self.assertEqual(len(groups),number_of_groups)
        for group in groups:
            self.assertEqual(group.matches.all().count(),number_of_matches)
   
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
            self.tournament.participating_players.add(user)
        
        
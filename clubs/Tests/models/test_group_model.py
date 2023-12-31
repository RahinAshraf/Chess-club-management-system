from django.test import TestCase
from clubs.models import Club, User, MembershipType, Tournament, Match,Group,Round
from ...Constants import consts
from django.utils import timezone

class GroupModelTestCase(TestCase):
    """ Unit tests of the group models """

    fixtures = ['clubs/Tests/fixtures/default_user.json','clubs/Tests/fixtures/default_set_up_of_clubs_and_tournament_with_owners_and_officers.json']

    def setUp(self):
        self.user = User.objects.get(first_name = "Russell")
        self.club = Club.objects.get(pk = 'Kerbal Chess Club')
        self.user2 = User.objects.get(first_name = 'John')

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

        self.Tournament = Tournament.objects.get(pk = 1)

        self.tournament_of_size_32 = Tournament.objects.create(club = self.club, name='Tournament1',
                                                    description = 'Description1',
                                                    capacity = '37',
                                                    organising_officer = self.officer,
                                                    deadline_to_apply = '2021-12-05 23:59')

        self.tournament_of_size_68 = Tournament.objects.create(club = self.club, name='Tournament1',
                                                    description = 'Description1',
                                                    capacity = '77',
                                                    organising_officer = self.officer,
                                                    deadline_to_apply = '2021-12-05 23:59')

        self.match=Match.objects.create(id='1',player1=self.user,player2=self.user2,date=timezone.now())

        #self.Tournament.save()
        self.round=Round(Tournament=self.Tournament)
        self.round.save()
        self.group=Group(Tournament=self.Tournament)
        self.group.save()


    def test_match_is_made(self):
        self._create_test_users()
        self.group.createMatches()
        self.assertEquals(self.group.matches.count(),6)

    def test_decide_winners(self):
        self._create_test_users()
        self.group.createMatches()
        self.assertEqual(self.group.matches.count(),6)
        self._create_test_match_results()
        self.group.decideWinners()
        self.assertEqual(self.group.winners.all().count(),2)

    def test_winners_are_not_decided_if_all_matches_have_not_occurred(self):
        self._create_test_users(user_count=32)
        self.group.createMatches()
        match = self.group.matches.all()[0]
        match.put_score_for_player(round = self.group, score = 1,player=match.player1)
        match.put_score_for_player(round = self.group, score = 0,player=match.player2)
        self.group.decideWinners()
        self.assertEqual(self.group.Tournament.participating_players.all().count(),32)

    def test_decide_winners_for_zero_matches(self):
        self._create_test_users(user_count=32)
        self.group.decideWinners()
        self.assertEqual(self.group.Tournament.participating_players.all().count(),32)

    def _create_test_users(self, user_count=4):
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
            self.group.players.add(user)
            self.Tournament.participating_players.add(user)

    def _create_test_match_results(self):
        for match in self.group.matches.all():
            match.put_score_for_player(round=self.group, score=1, player=match.player1)
            match.put_score_for_player2(round=self.group,score=0)

    #######Test for possibility to draw in a group stage match

    def create_and_join_32_users_for_tournament(self, user_count=32):
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
            self.tournament_of_size_32.participating_players.add(user)

    def create_and_join_68_users_for_tournament(self, user_count=68):
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
            self.tournament_of_size_68.participating_players.add(user)

    def help_draw_match(self):
        try:
            self.match.put_score_for_player(round = self.round, score = 0.5,player=self.user) #draws are permissible for tournaments with group stages
            self.match.put_score_for_player2(round = self.round, score = 0.5)
        except:
            self.fail('Scoring players for a tournament of size 32 is possible')

    def test_score_for_players_in_a_tournament_of_size_of_32(self):
        self.create_and_join_32_users_for_tournament()
        self.tournament_of_size_32.participating_players.add(self.user)
        self.tournament_of_size_32.participating_players.add(self.user2)
        self.help_draw_match()

    def test_score_for_players_in_a_tournament_of_size_of_68(self):
        self.create_and_join_68_users_for_tournament()
        self.tournament_of_size_68.participating_players.add(self.user)
        self.tournament_of_size_68.participating_players.add(self.user2)
        self.help_draw_match()

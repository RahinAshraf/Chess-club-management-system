from django.test import TestCase
from clubs.models import Club, User, MembershipType, Tournament, Match,Group
from ...Constants import consts
from django.utils import timezone

class TournamentModelTestCase(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
                    first_name = 'Test',
                    last_name = 'Case',
                    email = 'testCase@example.com',
                    password = 'Password123',
                    public_bio = 'Hello!!',
                    chess_experience_level = 3,
                    personal_statement = 'I want to play chess!!')
        self.club = Club.objects.create(club_owner = self.user,name = "Club1.0", location = 'location1', 
                                        mission_statement = 'We want to allow all to play free chess')
        
        self.user2 = User.objects.create_user(
                    first_name = 'Test',
                    last_name = 'Case',
                    email = 'testCase2@example.com',
                    password = 'Password123',
                    public_bio = 'Hello!!',
                    chess_experience_level = 3,
                    personal_statement = 'I want to play chess!!')

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

        self.Tournament = Tournament(club = self.club, name='Tournament1',
                                                    description = 'Description1',
                                                    capacity = '12',
                                                    organising_officer = self.officer,
                                                    deadline_to_apply = '2021-12-05 23:59')

        self.match=Match(id='1',player1=self.user,player2=self.user2,date=timezone.now())


        self.Tournament.save()
        
        self.group=Group(Tournament=self.Tournament)
        self.group.save()

        self.group2=Group(Tournament=self.Tournament)
        self.group2.save()
        self.group.nextRound = self.group2

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

    def test_advance_to_next_round(self):
        self._create_test_users()
        self.group.createMatches()
        self.assertEqual(self.group.matches.count(),6)
        self._create_test_match_results()
        self.group.decideWinners()
        self.assertEqual(self.group.winners.all().count(),2)
        self.group.go_to_next_round(self.group.winners.all())
        self.assertEqual(self.group2.players.all().count(), 2)
        self.assertEqual(self.Tournament.participating_players.all().count(),2)

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
            match.put_score_for_player1(round = self.group, score = 1)
            match.put_score_for_player2(round = self.group, score = 0)

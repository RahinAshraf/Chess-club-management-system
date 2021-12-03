from django.test import TestCase
from clubs.models import Club, User, MembershipType, Tournament
from django.core.exceptions import ValidationError
from django.urls import reverse
from ...Constants import consts
class ShowTournamentTestCase(TestCase):

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
        

        self.officer = User.objects.create_user(
                    first_name = 'Test',
                    last_name = 'Case',
                    email = 'testCaseOfficer@example.com',
                    password = 'Password123',
                    public_bio = 'Hello!!',
                    chess_experience_level = 3,
                    personal_statement = 'I want to play chess!!')

        self.membership = MembershipType.objects.create(user = self.officer, club = self.club, type = consts.OFFICER)

        self.url = reverse('tournaments')
    
    def test_tournament_list_url(self):
        self.assertEqual(self.url,'/tournaments/')

    def test_get_tournament_list(self):
        self.client.login(email=self.officer.email, password='Password123')
        self._create_test_tournaments(15-1)
        response = self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament_list.html')
        self.assertEqual(len(response.context['tournaments']), 14)
        for tournament_id in range(15-1):
            self.assertContains(response, f'Tournament{tournament_id}')
            self.assertContains(response, f'Description{tournament_id}')

    def _create_test_tournaments(self, tournament_count=10):
        for tournament_id in range(tournament_count):
            self.Tournament = Tournament(club = self.club, name=f'Tournament{tournament_id}',
                                                    description = f'Description{tournament_id}',
                                                    capacity = '12',
                                                    organising_officer = self.officer,
                                                    deadline_to_apply = '2021-12-05 23:59')
            self.Tournament.save()

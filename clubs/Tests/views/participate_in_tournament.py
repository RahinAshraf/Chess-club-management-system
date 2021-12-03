from django.test import TestCase
from clubs.models import Club, User, MembershipType, Tournament
from django.core.exceptions import ValidationError
from django.urls import reverse
from ...Constants import consts

class ParticipateInTournament(TestCase):

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
                    first_name = 'JohnDoe',
                    last_name = 'Case',
                    email = 'testCaseOfficer@example.com',
                    password = 'Password123',
                    public_bio = 'Hello!!',
                    chess_experience_level = 3,
                    personal_statement = 'I want to play chess!!')

        self.tournament = Tournament.objects.create(
            id = '1',
            club = self.club,
            participating_players = self.user,
            name = 'Tournament1',
            description = 'Description1',
            capacity = '12',
            organising_officer = self.officer,
            co_organising_officers = self.user,
            deadline_to_apply = '2021-12-05 23:59'
        )

    
    def test_successful_addition_of_tournament(self):
        before_count = Tournament.objects.filter(club = self.tournament).count()
        response = self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('tournaments')
        after_count = Tournament.objects.filter(club = self.tournament).count()
        self.assertEqual(after_count, before_count+1)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

   
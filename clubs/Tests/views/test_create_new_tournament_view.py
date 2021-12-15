from django.test import TestCase
from clubs.models import Club, User, MembershipType, Tournament
from django.core.exceptions import ValidationError
from django.urls import reverse
from ...Constants import consts

class CreateNewTournament(TestCase):
    """ Unit tests of creating new tournaments """
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

        self.url = reverse('create_tournament')

        self.form_input = {
            'name': 'Tournament1',
            'description': 'Description1',
            'deadline_to_apply': '2021-12-05 23:59',
            'capacity':'12'
        }

    def test_create_tournament_url(self):
        """ Test case to check if the redirected url is equivalent to the
            expected url for creating a new tournament """
        self.assertEqual(self.url, '/create_new_tournament/')

    def test_successful_creation_of_tournament(self):
        """" Test case for successful creation of a tournament when all
             conditions are satisifed """
        before_count = Tournament.objects.filter(club = self.club).count()
        self.client.login(email=self.officer.email, password='Password123')
        response = self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('tournaments')
        after_count = Tournament.objects.filter(club = self.club).count()
        self.assertEqual(after_count, before_count+1)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_unsuccessful_creation_of_tournament(self):
        """" Test case for unsuccessful creation of a tournament required fileds
             are not entered correctly """
        self.form_input['capacity'] = ''
        before_count = Tournament.objects.filter(club = self.club).count()
        self.client.login(email=self.officer.email, password='Password123')
        response = self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Tournament.objects.filter(club = self.club).count()
        self.assertEqual(after_count, before_count)

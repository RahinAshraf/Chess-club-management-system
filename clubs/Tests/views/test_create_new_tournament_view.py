from django.test import TestCase
from clubs.models import Club, User, MembershipType, Tournament
from django.core.exceptions import ValidationError
from django.urls import reverse
from ...Constants import consts

class CreateNewTournament(TestCase):
    """ Unit tests of creating new tournaments """
    fixtures = ['clubs/Tests/fixtures/default_user.json','clubs/Tests/fixtures/default_set_up_of_clubs_and_tournament_with_owners_and_officers.json']
    def setUp(self):
        self.user = User.objects.get(first_name = "Russell")
        self.officer = User.objects.get(first_name = "Valentina")
        self.club = Club.objects.get(pk="Kerbal Chess Club")
        MembershipType.objects.create(user = self.user, club = self.club, type = consts.CLUB_OWNER)
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

    def test_redirect_url_when_creating_tournament_without_club_choice(self):
        self.client.login(email=self.officer.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        response_url = reverse('user_profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
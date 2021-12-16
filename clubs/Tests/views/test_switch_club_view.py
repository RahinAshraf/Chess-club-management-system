from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from django.http import QueryDict
from ...Constants import consts
from ...models import Tournament, User,MembershipType,Club

class SwitchClubViewTestCase(TestCase):
    """ Tests of the switch club view """
    fixtures = ['clubs/Tests/fixtures/default_user.json','clubs/Tests/fixtures/default_set_up_of_clubs_and_tournament_with_owners_and_officers.json']
    def setUp(self):
        # self.owner = User.objects.create_user(
        #     email="owner@example.org",
        #     password="Pass123",
        #     first_name="ownerFirst",
        #     last_name="ownerLast",
        #     public_bio="owner",
        #     chess_experience_level=1,
        #     personal_statement="ownerPersonal",
        # )
        # self.club = Club.objects.create(club_owner=self.owner, name = "Club1", location = 'location1',
        #     mission_statement = 'We want to allow all to play free chess')
        self.owner = User.objects.get(first_name = "Russell")
        self.club = Club.objects.get(pk = 'Kerbal Chess Club')
        MembershipType.objects.create(user=self.owner, type=consts.CLUB_OWNER,club=self.club)
        self.client.login(email=self.owner.email, password='Password123')
        self.client.get('user_profile/', follow = True)

    def test_switch_club(self):
        """ Test case for switching clubs when the user is logged in """
        response = self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        response_url = reverse('user_profile')
        reponse_request = response.wsgi_request

        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertEqual(reponse_request.session['club_choice'], self.club.name)

    def test_redirect_url_for_user_list_when_club_is_not_chosen(self):
        response = self.client.get('/users/', follow=True)
        response_url = reverse('user_profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
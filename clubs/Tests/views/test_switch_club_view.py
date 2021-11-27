from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from django.http import QueryDict
from ...Constants import consts
from ...models import User,MembershipType,Club

class SwitchClubViewTestCase(TestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.org",
            password="Pass123",
            first_name="ownerFirst",
            last_name="ownerLast",
            public_bio="owner",
            chess_experience_level=1,
            personal_statement="ownerPersonal",
        )
        self.club = Club.objects.create(club_owner=self.owner, name = "Club1", location = 'location1',
            mission_statement = 'We want to allow all to play free chess')
        MembershipType.objects.create(user=self.owner,type=consts.CLUB_OWNER, club=self.club)

        self.client.login(email=self.owner.email, password='Pass123')
        self.client.get('test/', follow = True)

    def test_switch_club(self):
        response = self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        response_url = reverse('test')
        reponse_request = response.wsgi_request

        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertEqual(reponse_request.session['club_choice'], self.club.name)

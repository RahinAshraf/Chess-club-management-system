"""Unit tests of the log in form."""
from django import forms
from django.test import TestCase
from clubs.forms import CreateNewClubForm
from http import HTTPStatus
from clubs.models import Club, User
from clubs.views import password

class CreateNewClubFormTestCase(TestCase):
    """Unit tests of the log in form."""

    fixtures = ['clubs/Tests/fixtures/default_user.json','clubs/Tests/fixtures/default_set_up_of_clubs_and_tournament_with_owners_and_officers.json']

    def setUp(self):
        self.user = User.objects.get(first_name = "Russell")
        self.club = Club.objects.get(pk = 'Kerbal Chess Club')

        self.form_input= {
            "name":"Club23",
            "location": "locations1",
            "mission_statement":"Wwe want test"
        }

    def test_form_accepts_valid_input(self):
        form = CreateNewClubForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_name(self):
        self.form_input['name'] = ''
        form = CreateNewClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_location(self):
        self.form_input['location'] = ''
        form = CreateNewClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_mission_statement(self):
        self.form_input['mission_statement'] = ''
        form = CreateNewClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_correctly_assignes_club_owner(self):
        form = CreateNewClubForm(data=self.form_input)
        club = form.save(commit=False)
        club.club_owner = self.user
        club.save()
        form.save()
        club_owner = Club.objects.get(pk = self.form_input['name']).club_owner
        self.assertEqual(club_owner,self.user)

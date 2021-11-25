"""Unit tests of the log in form."""
from django import forms
from django.test import TestCase
from clubs.forms import CreateNewClubForm
from http import HTTPStatus
from clubs.models import Club, User


from clubs.views import password

class CreateNewClubFormTestCase(TestCase):
    """Unit tests of the log in form."""
    def setUp(self):
        self.user = User.objects.create_user(
                    first_name = 'Test',
                    last_name = 'Case',
                    email = 'testCase2@example.com',
                    password = 'Password123',
                    public_bio = 'Hello!!',
                    chess_experience_level = 3,
                    personal_statement = 'I want to play chess!!')
        self.club = Club.objects.create(club_owner =self.user,name = "Club1", location = 'location1', 
        mission_statement = 'We want to allow all to play free chess')
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

    

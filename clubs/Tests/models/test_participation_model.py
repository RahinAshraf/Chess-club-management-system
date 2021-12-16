from django.test import TestCase
from clubs.models import Club, User, MembershipType, Tournament, Match, Participation
from django.core.exceptions import ValidationError
from ...Constants import consts

class TestParticipationModel(TestCase):
    """ Unit tests of the participation model """

    fixtures = ['clubs/Tests/fixtures/default_user.json','clubs/Tests/fixtures/default_set_up_of_clubs_and_tournament_with_owners_and_officers.json']

    def setUp(self):
        self.user = User.objects.get(first_name = "Russell")
        self.club = Club.objects.get(pk = 'Kerbal Chess Club')
        self.Tournament = Tournament.objects.get(pk = 1)

        self.officer = User.objects.create_user(
                    first_name = 'Test',
                    last_name = 'Case',
                    email = 'testCaseOfficer@example.com',
                    password = 'Password123',
                    public_bio = 'Hello!!',
                    chess_experience_level = 3,
                    personal_statement = 'I want to play chess!!')

        self.membership = MembershipType.objects.create(user = self.officer, club = self.club, type = consts.OFFICER)
        
        self.Tournament.participating_players.add(self.user)

    def test_user_has_participation_when_being_added_to_tournament_participating_players(self):
        try:
            Participation.objects.get(user = self.user)
        except:
            self.fail('User should automatically have participation.')

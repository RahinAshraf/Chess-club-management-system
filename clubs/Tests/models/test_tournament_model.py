from django.test import TestCase
from clubs.models import Club, User, MembershipType, Tournament
from django.core.exceptions import ValidationError
from ...Constants import consts
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
        

        self.officer = User.objects.create_user(
                    first_name = 'Test',
                    last_name = 'Case',
                    email = 'testCaseOfficer@example.com',
                    password = 'Password123',
                    public_bio = 'Hello!!',
                    chess_experience_level = 3,
                    personal_statement = 'I want to play chess!!')

        self.membership = MembershipType.objects.create(user = self.officer, club = self.club, type = consts.OFFICER)

        self.Tournament = Tournament(club = self.club, name='Tournament1',
                                                    description = 'Description1',
                                                    capacity = '12',
                                                    organising_officer = self.officer,
                                                    deadline_to_apply = '2021-12-05 23:59')
        self.Tournament.save()
        
    
    def test_valid_tournament(self):
        try:
            self.Tournament.full_clean()
        except (ValidationError) :
            self.fail('Test tournament should be valid')

    def _assert_invalid_tournament(self):
        self.assertRaises(ValidationError,self.save())

    def test_users_more_than_capacity(self):
        self._create_test_users(user_count=int(self.Tournament.capacity))
        membership_list = MembershipType.objects.filter(club = self.club, type = consts.MEMBER)

        for membership in membership_list:
            self.Tournament.participating_players.add(membership.user)
            self.Tournament.save()

        # Adding the extra player
        with self.assertRaises(ValidationError):
            self.Tournament.participating_players.add(self.user)
            self.Tournament.save()

    def test_organiser_cannot_be_a_participating_player(self):
        with self.assertRaises(ValidationError):
            self.Tournament.participating_players.add(self.officer)
            self.Tournament.save()

    def test_organizer_must_be_an_officer(self):
        with self.assertRaises(ValidationError):
            self.Tournament.organising_officer = self.user
            self.Tournament.save()

    def _create_test_users(self, user_count=10):
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
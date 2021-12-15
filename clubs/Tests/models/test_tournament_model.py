from django.test import TestCase
from clubs.models import Club, User, MembershipType, Tournament, Match, Participation
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
        
        self.user2 = User.objects.create_user(
                    first_name = 'Test',
                    last_name = 'Case',
                    email = 'testCase2@example.com',
                    password = 'Password123',
                    public_bio = 'Hello!!',
                    chess_experience_level = 3,
                    personal_statement = 'I want to play chess!!')

        self.officer = User.objects.create_user(
                    first_name = 'Test',
                    last_name = 'Case',
                    email = 'testCaseOfficer@example.com',
                    password = 'Password123',
                    public_bio = 'Hello!!',
                    chess_experience_level = 3,
                    personal_statement = 'I want to play chess!!')

        self.membership = MembershipType.objects.create(user = self.officer, club = self.club, type = consts.OFFICER)

        self.membership2 = MembershipType.objects.create(user = self.user2, club = self.club, type = consts.OFFICER)

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
       with self.assertRaises(ValidationError):
           self.Tournament.save()

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

    def test_participation_for_users_in_tournaments(self):
        self._create_test_users()
        membership_list = MembershipType.objects.filter(club = self.club, type = consts.MEMBER)

        for membership in membership_list:
            self.Tournament.participating_players.add(membership.user)
            self.Tournament.save()

        self.assertEqual(Participation.objects.filter(tournament = self.Tournament).count(),10)

    def test_participation_for_users_when_user_is_not_in_tournament_participating_player_list(self):
        """This tests if a loser of a match in a tournament is removed from the participating list
        the participation record for that user still remains."""
        self.Tournament.participating_players.add(self.user)
        self.Tournament.participating_players.add(self.user2)

        # removing user 2
        self.Tournament.participating_players.remove(self.user2)

        # cheking if participation exists.
        try:
            Participation.objects.get(user = self.user2)
        except:
            self.fail('Participation object should exist.')

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

    def test_co_organisers_cannot_be_a_participating_player(self):
        # Creating a co organiser
       co_organiser = User.objects.create_user(
                    first_name = 'Test',
                    last_name = 'Case',
                    email = 'testCaseOfficerCoOrganiser@example.com',
                    password = 'Password123',
                    public_bio = 'Hello!!',
                    chess_experience_level = 3,
                    personal_statement = 'I want to play chess!!')

       MembershipType.objects.create(club = self.club, user = co_organiser, type = consts.OFFICER)
       self.Tournament.co_organising_officers.add(co_organiser) 
       self.Tournament.participating_players.add(co_organiser)
       self._assert_invalid_tournament()

    def test_co_organisers_should_be_an_officer(self):
        co_organiser = User.objects.create_user(
                    first_name = 'Test',
                    last_name = 'Case',
                    email = 'testCaseOfficerCoOrganiser@example.com',
                    password = 'Password123',
                    public_bio = 'Hello!!',
                    chess_experience_level = 3,
                    personal_statement = 'I want to play chess!!')

        MembershipType.objects.create(club = self.club, user = co_organiser, type = consts.MEMBER)
        self.Tournament.co_organising_officers.add(co_organiser) 
        self._assert_invalid_tournament()

    def test_organiser_cannot_be_a_part_of_any_match(self):
        match = Match.objects.create(date = '2021-12-17', player1 = self.officer, player2 = self.user2)
        self.Tournament.matches.add(match)
        self._assert_invalid_tournament()

    def test_co_organiser_cannot_ba_a_part_of_any_match(self):
        co_organiser = User.objects.create_user(
                    first_name = 'Test',
                    last_name = 'Case',
                    email = 'testCaseOfficerCoOrganiser@example.com',
                    password = 'Password123',
                    public_bio = 'Hello!!',
                    chess_experience_level = 3,
                    personal_statement = 'I want to play chess!!')

        MembershipType.objects.create(club = self.club, user = co_organiser, type = consts.MEMBER)
        self.Tournament.co_organising_officers.add(co_organiser) 
        match = Match.objects.create(date = '2021-12-17', player1 = co_organiser, player2 = self.user2)
        self.Tournament.matches.add(match)
        self._assert_invalid_tournament()

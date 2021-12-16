from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from ...Constants import consts
from ...models import User,MembershipType,Club

class PromoteViewTestCase(TestCase):
    """ Unit tests of promoting users within a club """
    def setUp(self):
        self.officer = User.objects.create_user(
            email="officer@example.org",
            password="Pass123",
            first_name="officerFirst",
            last_name="officerLast",
            public_bio="officer",
            chess_experience_level=1,
            personal_statement="officerPersonal",
        )
        self.owner = User.objects.create_user(
            email="owner@example.org",
            password="Pass123",
            first_name="ownerFirst",
            last_name="ownerLast",
            public_bio="owner",
            chess_experience_level=1,
            personal_statement="owner",
        )
        self.club = Club.objects.create(club_owner=self.owner,name = "Club1", location = 'location1',
            mission_statement = 'We want to allow all to play free chess')
        MembershipType.objects.create(user=self.officer,type=consts.OFFICER, club=self.club)
        self.client.login(email=self.officer.email, password='Pass123')


        self.applicant = User.objects.create_user(
            email="applicant@example.org",
            password="Pass123",
            first_name="applicantFirst",
            last_name="applicantLast",
            public_bio="applicant",
            chess_experience_level=1,
            personal_statement="applicantPersonal",
        )
        MembershipType.objects.create(user=self.applicant, type=consts.APPLICANT, club=self.club)

        self.url = reverse("promote",kwargs={"user_id":self.applicant.pk})


    def test_promote_url(self):
        """ Test case to check if the redirected url is equivalent to the
        expected url for promoting a user within club """
        self.assertEqual(self.url, "/promote/" + str(self.applicant.pk) + "/")


    def test_promote_successful(self):
        """" Test case for successfully promoting a user in club when all
         conditions are satisifed """
        applicantType = MembershipType.objects.get(user = self.applicant, club = self.club).type
        self.assertEqual(applicantType, consts.APPLICANT)
        response = self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        response = self.client.get(self.url, follow=True)

        applicantType = MembershipType.objects.get(user = self.applicant, club = self.club).type
        self.assertEqual(applicantType, consts.MEMBER)

        response_url = reverse("user_list")
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        messages_list = list(response.context["messages"])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)


    def test_promote_nonexisting_user(self):
        """" Test case for attempting to demote a non-existing user in club """
        userLength = len(User.objects.all())
        self.url = reverse("promote",kwargs={"user_id": userLength+1})
        response = self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        response = self.client.get(self.url, follow=True)

        response_url = reverse("user_list")
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        messages_list = list(response.context["messages"])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)


    def test_cannot_promote(self):
        """" Test case for unsuccussfully promoting a user when the request user
             is a member instead of a officier """
        self.client.login(email=self.applicant.email, password='Pass123')
        response = self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        response = self.client.get(self.url, follow=True)

        response_url = reverse("user_list")
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        messages_list = list(response.context["messages"])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)


    def test_promote_member(self):
        
        applicantMembership = MembershipType.objects.get(user = self.applicant, club = self.club)
        applicantMembership.type = "member"
        applicantMembership.save()

        applicantType = MembershipType.objects.get(user = self.applicant, club = self.club).type
        self.assertEqual(applicantType, consts.MEMBER)

        response = self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        response = self.client.get(self.url, follow=True)

        applicantType = MembershipType.objects.get(user = self.applicant, club = self.club).type
        self.assertEqual(applicantType, consts.OFFICER)

        response_url = reverse("user_list")
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        messages_list = list(response.context["messages"])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

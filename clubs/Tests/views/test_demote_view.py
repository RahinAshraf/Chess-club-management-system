from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from ...Constants import consts
from ...models import User,MembershipType, Club

class demoteViewTestCase(TestCase):

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
        self.club = Club.objects.create(name = "Club1", location = 'location1', 
            mission_statement = 'We want to allow all to play free chess')
        MembershipType.objects.create(user=self.officer,type=consts.OFFICER, club=self.club)

        self.club_owner = User.objects.create_user(
            email="clubOwner@example.org",
            password="Pass123",
            first_name="clubOwnerFirst",
            last_name="clubOwnerLast",
            public_bio="club_owner",
            chess_experience_level=1,
            personal_statement="clubOwnerPersonal",
        )
        MembershipType.objects.create(user=self.club_owner, type=consts.CLUB_OWNER, club=self.club)
        self.client.login(email=self.club_owner.email, password='Pass123')

        self.url = reverse("demote",kwargs={"user_id":self.officer.pk})

    def test_demote_url(self):
        self.assertEqual(self.url, "/demote/" + str(self.officer.pk) + "/")

    def test_demote_successful(self):
        officerType = MembershipType.objects.get(user = self.officer).type
        self.assertEqual(officerType, consts.OFFICER)

        response = self.client.get(self.url, follow=True)

        officerType = MembershipType.objects.get(user = self.officer).type
        self.assertEqual(officerType, consts.MEMBER)

        response_url = reverse("user_list")
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        messages_list = list(response.context["messages"])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

    def test_demote_nonexisting_user(self):
        userLength = len(User.objects.all())
        self.url = reverse("demote",kwargs={"user_id": userLength+1})
        response = self.client.get(self.url, follow=True)

        response_url = reverse("user_list")
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        messages_list = list(response.context["messages"])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_cannot_demote(self):
        self.client.login(email=self.officer.email, password='Pass123')
        response = self.client.get(self.url, follow=True)

        response_url = reverse("user_list")
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        messages_list = list(response.context["messages"])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

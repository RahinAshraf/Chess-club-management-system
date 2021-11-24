from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from ...Constants import consts
from ...models import User,MembershipType

class PromoteViewTestCase(TestCase):

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
        MembershipType.objects.create(user=self.officer,type=consts.OFFICER)
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
        MembershipType.objects.create(user=self.applicant, type=consts.APPLICANT)

        self.url = reverse("promote",kwargs={"user_id":self.applicant.pk})


    def test_promote_url(self):
        self.assertEqual(self.url, "/promote/" + str(self.applicant.pk) + "/")


    def test_promote_successful(self):
        applicantType = MembershipType.objects.get(pk=self.applicant.pk).type
        self.assertEqual(applicantType, consts.APPLICANT)

        response = self.client.get(self.url, follow=True)

        applicantType = MembershipType.objects.get(pk=self.applicant.pk).type
        self.assertEqual(applicantType, consts.MEMBER)

        response_url = reverse("user_list")
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        messages_list = list(response.context["messages"])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)


    def test_promote_nonexisting_user(self):
        userLength = len(User.objects.all())
        self.url = reverse("promote",kwargs={"user_id": userLength+1})
        response = self.client.get(self.url, follow=True)

        response_url = reverse("user_list")
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        messages_list = list(response.context["messages"])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)


    def test_cannot_promote(self):
        self.client.login(email=self.applicant.email, password='Pass123')
        response = self.client.get(self.url, follow=True)

        response_url = reverse("user_list")
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        messages_list = list(response.context["messages"])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)


    def test_promote_member(self):
        applicantMembership = MembershipType.objects.get(pk=self.applicant.pk)
        applicantMembership.type = "member"
        applicantMembership.save()

        applicantType = MembershipType.objects.get(pk=self.applicant.pk).type
        self.assertEqual(applicantType, consts.MEMBER)

        response = self.client.get(self.url, follow=True)

        applicantType = MembershipType.objects.get(pk=self.applicant.pk).type
        self.assertEqual(applicantType, consts.OFFICER)

        response_url = reverse("user_list")
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        messages_list = list(response.context["messages"])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.INFO)

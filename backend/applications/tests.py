
from datetime import date, timedelta

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from scholarships.models import Scholarship
from .models import Application


class ApplicationAPITests(APITestCase):

    def setUp(self):
        self.student = User.objects.create_user(
            username="student1",
            password="testpass123"
        )

        self.other_student = User.objects.create_user(
            username="student2",
            password="testpass123"
        )

        self.scholarship = Scholarship.objects.create(
            name="Merit Scholarship",
            provider="Test Foundation",
            description="Scholarship for deserving students",
            amount=10000,
            deadline=date.today() + timedelta(days=30),
            status="active"
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.student)

        self.list_url = "/api/applications/"

    def test_create_application(self):
        response = self.client.post(
            self.list_url,
            {"scholarship": self.scholarship.id},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Application.objects.count(), 1)
        self.assertEqual(
            Application.objects.first().student,
            self.student
        )

    def test_list_applications(self):
        Application.objects.create(
            student=self.student,
            scholarship=self.scholarship
        )

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_application(self):
        application = Application.objects.create(
            student=self.student,
            scholarship=self.scholarship
        )

        response = self.client.get(
            f"{self.list_url}{application.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], application.id)

    def test_update_application(self):
        application = Application.objects.create(
            student=self.student,
            scholarship=self.scholarship
        )

        response = self.client.patch(
            f"{self.list_url}{application.id}/",
            {
                "status": "APPLIED",
                "notes": "Application submitted"
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        application.refresh_from_db()

        self.assertEqual(application.status, "APPLIED")
        self.assertEqual(application.notes, "Application submitted")

    def test_duplicate_application(self):
        Application.objects.create(
            student=self.student,
            scholarship=self.scholarship
        )

        response = self.client.post(
            self.list_url,
            {"scholarship": self.scholarship.id},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_access_other_students_application(self):
        application = Application.objects.create(
            student=self.other_student,
            scholarship=self.scholarship
        )

        response = self.client.get(
            f"{self.list_url}{application.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

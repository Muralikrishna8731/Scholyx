
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

from scholarships.models import Scholarship

from .models import StudentProfile


class AdminInterfaceTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="AdminPass!2026",
        )
        self.student = User.objects.create_user(
            username="student_admin_test",
            email="student@example.com",
            password="StudentPass!2026",
        )
        self.profile = StudentProfile.objects.create(
            user=self.student,
            full_name="Admin Test Student",
            college="Test College",
        )

        self.scholarship = Scholarship.objects.create(
            name="Admin Test Scholarship",
            provider="Test Foundation",
            description="Test scholarship",
            amount="5000.00",
            deadline="2027-12-31",
            status=Scholarship.Status.ACTIVE,
        )

    def test_admin_dashboard_displays_platform_counts(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Registered students")
        self.assertContains(response, "Active scholarships")
        self.assertContains(response, "Applied applications")

    def test_student_cannot_access_admin(self):
        self.client.force_login(self.student)

        response = self.client.get(reverse("admin:index"))

        self.assertIn(response.status_code, (302, 403))

    def test_admin_can_search_and_open_student_profile(self):
        self.client.force_login(self.admin)

        search_url = reverse("admin:accounts_studentprofile_changelist")
        response = self.client.get(search_url, {"q": "student_admin_test"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin Test Student")

        detail_url = reverse(
            "admin:accounts_studentprofile_change",
            args=(self.profile.pk,),
        )
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Application history")


class StudentRegistrationTests(APITestCase):
    def setUp(self):
        self.url = reverse("register")
        self.valid_data = {
            "username": "madhura_test",
            "email": "madhura_test@example.com",
            "password": "StrongPass!2026",
            "full_name": "Test Student",
        }

    def test_successful_registration(self):
        response = self.client.post(
            self.url, self.valid_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(StudentProfile.objects.count(), 1)

        user = User.objects.get(username="madhura_test")
        self.assertEqual(user.email, "madhura_test@example.com")
        self.assertTrue(user.check_password("StrongPass!2026"))
        self.assertNotEqual(user.password, "StrongPass!2026")
        self.assertNotIn("password", response.data)

    def test_duplicate_username_is_rejected(self):
        User.objects.create_user(
            username="madhura_test",
            email="existing@example.com",
            password="AnotherStrong!2026",
        )

        response = self.client.post(
            self.url, self.valid_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(StudentProfile.objects.count(), 0)

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(
            username="existing_user",
            email="madhura_test@example.com",
            password="AnotherStrong!2026",
        )

        response = self.client.post(
            self.url, self.valid_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(StudentProfile.objects.count(), 0)

    def test_invalid_email_is_rejected(self):
        data = {**self.valid_data, "email": "invalid-email"}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(StudentProfile.objects.count(), 0)

    def test_weak_password_is_rejected(self):
        data = {**self.valid_data, "password": "123"}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(StudentProfile.objects.count(), 0)

    def test_missing_full_name_is_rejected(self):
        data = {**self.valid_data}
        data.pop("full_name")

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(StudentProfile.objects.count(), 0)





class JWTAuthenticationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="jwt_test",
            email="jwt_test@example.com",
            password="StrongTestPass!2026",
        )

        StudentProfile.objects.create(
            user=self.user,
            full_name="JWT Test Student",
        )

        self.scholarship = Scholarship.objects.create(
            name="JWT Test Scholarship",
            provider="Test Provider",
            description="Scholarship for authentication testing.",
            amount="1000.00",
            deadline="2027-12-31",
            status=Scholarship.Status.ACTIVE,
        )

        self.login_url = reverse("token_obtain_pair")
        self.refresh_url = reverse("token_refresh")
        self.logout_url = reverse("logout")
        self.protected_url = reverse(
            "scholarship-eligibility",
            kwargs={"scholarship_id": self.scholarship.id},
        )


    def test_valid_login_returns_access_and_refresh_tokens(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "jwt_test",
                "password": "StrongTestPass!2026",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_invalid_password_is_rejected(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "jwt_test",
                "password": "wrong-password",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_returns_new_access_token(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "jwt_test",
                "password": "StrongTestPass!2026",
            },
            format="json",
        )
        refresh_token = response.data["refresh"]

        refresh_response = self.client.post(
            self.refresh_url,
            {"refresh": refresh_token},
            format="json",
        )

        self.assertEqual(
            refresh_response.status_code, status.HTTP_200_OK
        )
        self.assertIn("access", refresh_response.data)

    def test_authenticated_user_can_logout_and_blacklist_refresh_token(self):
        login_response = self.client.post(
            self.login_url,
            {
                "username": "jwt_test",
                "password": "StrongTestPass!2026",
            },
            format="json",
        )
        refresh_token = login_response.data["refresh"]
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}"
        )

        response = self.client.post(
            self.logout_url,
            {"refresh": refresh_token},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(BlacklistedToken.objects.count(), 1)
        self.assertEqual(
            self.client.get(self.protected_url).status_code,
            status.HTTP_200_OK,
        )

    def test_blacklisted_refresh_token_cannot_be_reused(self):
        login_response = self.client.post(
            self.login_url,
            {
                "username": "jwt_test",
                "password": "StrongTestPass!2026",
            },
            format="json",
        )
        refresh_token = login_response.data["refresh"]
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}"
        )

        logout_response = self.client.post(
            self.logout_url,
            {"refresh": refresh_token},
            format="json",
        )
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)

        refresh_response = self.client.post(
            self.refresh_url,
            {"refresh": refresh_token},
            format="json",
        )

        self.assertEqual(
            refresh_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_logout_rejects_unauthenticated_request(self):
        response = self.client.post(
            self.logout_url,
            {"refresh": "not-a-valid-token"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_logout_rejects_invalid_refresh_token(self):
        login_response = self.client.post(
            self.login_url,
            {
                "username": "jwt_test",
                "password": "StrongTestPass!2026",
            },
            format="json",
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}"
        )

        response = self.client.post(
            self.logout_url,
            {"refresh": "not-a-valid-token"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_logout_rejects_another_users_refresh_token(self):
        other_user = User.objects.create_user(
            username="other_jwt_test",
            email="other_jwt_test@example.com",
            password="AnotherStrongPass!2026",
        )
        other_login_response = self.client.post(
            self.login_url,
            {
                "username": other_user.username,
                "password": "AnotherStrongPass!2026",
            },
            format="json",
        )
        login_response = self.client.post(
            self.login_url,
            {
                "username": "jwt_test",
                "password": "StrongTestPass!2026",
            },
            format="json",
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}"
        )

        response = self.client.post(
            self.logout_url,
            {"refresh": other_login_response.data["refresh"]},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        refresh_response = self.client.post(
            self.refresh_url,
            {"refresh": other_login_response.data["refresh"]},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)


    def test_protected_endpoint_rejects_unauthenticated_request(self):
        response = self.client.get(self.protected_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


    def test_protected_endpoint_accepts_valid_access_token(self):
        login_response = self.client.post(
            self.login_url,
            {
                "username": "jwt_test",
                "password": "StrongTestPass!2026",
            },
            format="json",
        )

        access_token = login_response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        response = self.client.get(self.protected_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

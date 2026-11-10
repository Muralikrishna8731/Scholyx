from decimal import Decimal

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import (
	Branch,
	Category,
	Course,
	District,
	RequiredDocument,
	Scholarship,
	State,
)


class ScholarshipModelTests(TestCase):
	def create_scholarship(self, **overrides):
		values = {
			"name": "Future Scholars Award",
			"provider": "Scholyx Foundation",
			"description": "Support for eligible students.",
			"amount": Decimal("1000.00"),
			"deadline": "2027-06-30",
		}
		values.update(overrides)
		return Scholarship.objects.create(**values)

	def test_optional_eligibility_criteria_can_be_unspecified(self):
		scholarship = self.create_scholarship()

		self.assertIsNone(scholarship.minimum_percentage)
		self.assertIsNone(scholarship.minimum_cgpa)
		self.assertIsNone(scholarship.maximum_family_income)
		self.assertIsNone(scholarship.minimum_age)
		self.assertIsNone(scholarship.maximum_age)
		self.assertIsNone(scholarship.gender)
		self.assertIsNone(scholarship.year_of_study)
		self.assertIsNone(scholarship.pwd)
		self.assertIsNone(scholarship.minority)

	def test_lookup_relations_and_required_documents(self):
		scholarship = self.create_scholarship()
		category = Category.objects.create(name="General")
		state = State.objects.create(name="Karnataka")
		district = District.objects.create(name="Mysuru")
		course = Course.objects.create(name="Engineering")
		branch = Branch.objects.create(name="Computer Science")
		scholarship.category.add(category)
		scholarship.state.add(state)
		scholarship.district.add(district)
		scholarship.course.add(course)
		scholarship.branch.add(branch)
		document = RequiredDocument.objects.create(
			scholarship=scholarship,
			name="Income certificate",
		)

		self.assertEqual(scholarship.category.get(), category)
		self.assertEqual(scholarship.state.get(), state)
		self.assertEqual(scholarship.district.get(), district)
		self.assertEqual(scholarship.course.get(), course)
		self.assertEqual(scholarship.branch.get(), branch)
		self.assertEqual(scholarship.required_documents.get(), document)

	def test_amount_must_satisfy_database_constraint(self):
		with self.assertRaises(IntegrityError):
			with transaction.atomic():
				self.create_scholarship(amount=Decimal("0.00"))


class ScholarshipAPITests(APITestCase):
    def setUp(self):
        self.active_scholarship = Scholarship.objects.create(
            name="Active Scholarship",
            provider="Scholyx Foundation",
            description="Support for eligible students.",
            amount=Decimal("5000.00"),
            deadline="2027-06-30",
            application_url="https://example.com/apply",
            status=Scholarship.Status.ACTIVE,
            minimum_percentage=Decimal("75.00"),
            minimum_cgpa=Decimal("7.00"),
        )

        self.draft_scholarship = Scholarship.objects.create(
            name="Draft Scholarship",
            provider="Test Provider",
            description="Not yet available.",
            amount=Decimal("2000.00"),
            deadline="2027-12-31",
            status=Scholarship.Status.DRAFT,
        )

        self.closed_scholarship = Scholarship.objects.create(
            name="Closed Scholarship",
            provider="Test Provider",
            description="No longer available.",
            amount=Decimal("3000.00"),
            deadline="2027-01-31",
            status=Scholarship.Status.CLOSED,
        )

        self.list_url = reverse("scholarship-list")
        self.detail_url = reverse(
            "scholarship-detail",
            kwargs={"pk": self.active_scholarship.pk},
        )

    def test_listing_returns_only_active_scholarships(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["name"],
            "Active Scholarship",
        )

    def test_empty_listing_returns_empty_list(self):
        Scholarship.objects.all().delete()

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_detail_returns_scholarship_information(self):
        category = Category.objects.create(name="General")
        state = State.objects.create(name="Karnataka")

        self.active_scholarship.category.add(category)
        self.active_scholarship.state.add(state)

        RequiredDocument.objects.create(
            scholarship=self.active_scholarship,
            name="Income Certificate",
            description="Proof of family income.",
            is_mandatory=True,
        )

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["name"],
            "Active Scholarship",
        )
        self.assertEqual(
            response.data["application_url"],
            "https://example.com/apply",
        )
        self.assertEqual(
            response.data["minimum_percentage"],
            "75.00",
        )
        self.assertEqual(response.data["category"], ["General"])
        self.assertEqual(response.data["state"], ["Karnataka"])
        self.assertEqual(
            response.data["required_documents"][0]["name"],
            "Income Certificate",
        )
        self.assertTrue(
            response.data["required_documents"][0]["is_mandatory"]
        )

    def test_draft_scholarship_detail_returns_404(self):
        url = reverse(
            "scholarship-detail",
            kwargs={"pk": self.draft_scholarship.pk},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_closed_scholarship_detail_returns_404(self):
        url = reverse(
            "scholarship-detail",
            kwargs={"pk": self.closed_scholarship.pk},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_nonexistent_scholarship_returns_404(self):
        url = reverse(
            "scholarship-detail",
            kwargs={"pk": 999999},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ScholarshipSearchAPITests(APITestCase):
    def create_scholarship(self, **overrides):
        values = {
            "name": "Future Scholars Award",
            "provider": "Scholyx Foundation",
            "description": "Support for eligible students.",
            "amount": Decimal("1000.00"),
            "deadline": "2027-06-30",
            "status": Scholarship.Status.ACTIVE,
        }
        values.update(overrides)
        return Scholarship.objects.create(**values)

    def search(self, **params):
        return self.client.get(reverse("scholarship-list"), params)

    def test_search_matches_name_provider_and_description(self):
        name_match = self.create_scholarship(name="Merit award")
        provider_match = self.create_scholarship(
            name="Provider award",
            provider="Merit foundation",
        )
        description_match = self.create_scholarship(
            name="Description award",
            description="A merit-based opportunity.",
        )
        self.create_scholarship(
            name="Inactive merit award",
            status=Scholarship.Status.CLOSED,
        )

        for expected in (name_match, provider_match, description_match):
            with self.subTest(scholarship=expected.name):
                response = self.search(search="merit")
                self.assertEqual(response.status_code, 200)
                self.assertIn(
                    expected.pk,
                    [item["id"] for item in response.data],
                )
                self.assertEqual(len(response.data), 3)

    def test_amount_deadline_and_active_filters(self):
        target = self.create_scholarship(
            amount=Decimal("1000.00"),
            deadline="2026-06-30",
        )
        self.create_scholarship(
            name="Smaller award",
            amount=Decimal("500.00"),
            deadline="2027-06-30",
        )
        self.create_scholarship(
            name="Inactive award",
            status=Scholarship.Status.CLOSED,
        )

        for params in (
            {"amount": "1000"},
            {"min_amount": "750"},
            {"deadline_before": "2026-12-31"},
        ):
            with self.subTest(params=params):
                response = self.search(**params)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    [item["id"] for item in response.data],
                    [target.pk],
                )

        response = self.search()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_eligibility_filters_match_option_codes_and_values(self):
        target = self.create_scholarship(
            gender=Scholarship.Gender.FEMALE,
            year_of_study=Scholarship.YearOfStudy.FIRST,
        )
        options = {
            "course": (Course, "BE_BTECH", "Engineering"),
            "branch": (Branch, "CSE", "Computer Science"),
            "category": (Category, "OBC", "Other Backward Class"),
            "state": (State, "KA", "Karnataka"),
            "district": (District, "MYS", "Mysuru"),
        }
        for field_name, (model, code, name) in options.items():
            option = model.objects.create(code=code, name=name)
            getattr(target, field_name).add(option)

        self.create_scholarship(name="Unmatched scholarship")

        for field_name, (model, code, name) in options.items():
            for value in (code, name):
                with self.subTest(field=field_name, value=value):
                    response = self.search(**{field_name: value})
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(
                        [item["id"] for item in response.data],
                        [target.pk],
                    )

        for params in (
            {"gender": "female"},
            {"year_of_study": "1"},
        ):
            with self.subTest(params=params):
                response = self.search(**params)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    [item["id"] for item in response.data],
                    [target.pk],
                )

    def test_combined_filters_and_empty_results(self):
        target = self.create_scholarship(
            name="Merit engineering award",
            amount=Decimal("15000.00"),
            deadline="2026-10-01",
            gender=Scholarship.Gender.FEMALE,
            year_of_study=Scholarship.YearOfStudy.SECOND,
        )
        course = Course.objects.create(code="BE_BTECH", name="Engineering")
        category = Category.objects.create(code="OBC", name="OBC")
        state = State.objects.create(code="KA", name="Karnataka")
        target.course.add(course)
        target.category.add(category)
        target.state.add(state)
        self.create_scholarship(name="Other award")

        response = self.search(
            search="merit",
            min_amount="10000",
            deadline_before="2026-12-31",
            course="BE_BTECH",
            category="OBC",
            state="KA",
            gender="female",
            year_of_study="2",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["id"] for item in response.data], [target.pk])

        response = self.search(search="does-not-exist")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_invalid_query_values_return_bad_request(self):
        for params in (
            {"min_amount": "not-a-number"},
            {"deadline_before": "not-a-date"},
            {"gender": "invalid"},
            {"year_of_study": "9"},
            {"course": "UNKNOWN"},
        ):
            with self.subTest(params=params):
                response = self.search(**params)
                self.assertEqual(response.status_code, 400)

    def test_active_scholarship_detail_remains_available(self):
        active = self.create_scholarship()
        inactive = self.create_scholarship(
            name="Closed scholarship",
            status=Scholarship.Status.CLOSED,
        )

        response = self.client.get(f"/api/scholarships/{active.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], active.pk)

        response = self.client.get(f"/api/scholarships/{inactive.pk}/")
        self.assertEqual(response.status_code, 404)

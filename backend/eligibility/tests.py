
from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import StudentProfile
from scholarships.models import (
    Branch,
    Category,
    Course,
    District,
    Scholarship,
    State,
)
from .services import evaluate_eligibility


class EligibilityServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="eligibility_test",
            password="test-password",
        )

        self.student = StudentProfile.objects.create(
            user=self.user,
            full_name="Test Student",
            percentage=Decimal("85.00"),
        )

        self.scholarship = Scholarship.objects.create(
            name="Test Scholarship",
            provider="Test Provider",
            description="Eligibility service test",
            amount=Decimal("5000.00"),
            deadline=date(2027, 12, 31),
            status=Scholarship.Status.ACTIVE,
            minimum_percentage=Decimal("75.00"),
        )

    def test_percentage_requirement_passes(self):
        result = evaluate_eligibility(self.scholarship, self.student)

        self.assertEqual(
            result["criteria"]["percentage"]["status"],
            "passed",
        )
        self.assertEqual(result["overall_status"], "eligible")
    
    def test_percentage_requirement_fails(self):
        self.scholarship.minimum_percentage = Decimal("90.00")
        self.scholarship.save()

        result = evaluate_eligibility(self.scholarship, self.student)

        self.assertEqual(
            result["criteria"]["percentage"]["status"],
            "failed",
        )
        self.assertEqual(result["overall_status"], "ineligible")
    
    def test_missing_percentage_returns_incomplete(self):
        self.student.percentage = None
        self.student.save()

        result = evaluate_eligibility(self.scholarship, self.student)

        self.assertEqual(
            result["criteria"]["percentage"]["status"],
            "unknown",
        )
        self.assertEqual(result["overall_status"], "incomplete")

    
    def test_cgpa_requirement_passes(self):
        self.scholarship.minimum_cgpa = Decimal("7.00")
        self.scholarship.save()

        self.student.cgpa = Decimal("8.20")
        self.student.save()

        result = evaluate_eligibility(self.scholarship, self.student)

        self.assertEqual(
            result["criteria"]["cgpa"]["status"],
            "passed",
        )
        self.assertEqual(result["overall_status"], "eligible")

    
    def test_family_income_requirement_passes(self):
        self.scholarship.maximum_family_income = Decimal("250000.00")
        self.scholarship.save()

        self.student.family_income = Decimal("200000.00")
        self.student.save()

        result = evaluate_eligibility(self.scholarship, self.student)

        self.assertEqual(
            result["criteria"]["family_income"]["status"],
            "passed",
        )
        self.assertEqual(result["overall_status"], "eligible")

    
    def test_age_requirement_passes(self):
        today = date.today()
        self.student.date_of_birth = date(
            today.year - 20,
            today.month,
            today.day,
        )
        self.student.save()

        self.scholarship.minimum_age = 18
        self.scholarship.maximum_age = 25
        self.scholarship.save()

        result = evaluate_eligibility(self.scholarship, self.student)

        self.assertEqual(
            result["criteria"]["age"]["status"],
            "passed",
        )
        self.assertEqual(result["overall_status"], "eligible")

    
    def test_category_requirement_passes(self):
        from scholarships.models import Category

        category = Category.objects.create(
            code="OBC",
            name="Other Backward Classes",
        )
        self.scholarship.category.add(category)

        self.student.category = "OBC"
        self.student.save()

        result = evaluate_eligibility(self.scholarship, self.student)

        self.assertEqual(
            result["criteria"]["category"]["status"],
            "passed",
        )
        self.assertEqual(result["overall_status"], "eligible")

    
    def test_category_requirement_fails(self):
        from scholarships.models import Category

        category = Category.objects.create(
            code="SC",
            name="Scheduled Caste",
        )
        self.scholarship.category.add(category)

        self.student.category = "OBC"
        self.student.save()

        result = evaluate_eligibility(self.scholarship, self.student)

        self.assertEqual(
            result["criteria"]["category"]["status"],
            "failed",
        )
        self.assertEqual(result["overall_status"], "ineligible")

    
    def test_state_requirement_passes(self):
        from scholarships.models import State

        state = State.objects.create(
            code="KARNATAKA",
            name="Karnataka",
        )
        self.scholarship.state.add(state)

        self.student.state = "KARNATAKA"
        self.student.save()

        result = evaluate_eligibility(self.scholarship, self.student)

        self.assertEqual(
            result["criteria"]["state"]["status"],
            "passed",
        )
        self.assertEqual(result["overall_status"], "eligible")
    
    def test_district_requirement_passes(self):
        from scholarships.models import District

        district = District.objects.create(
            code="MYSURU",
            name="Mysuru",
        )
        self.scholarship.district.add(district)
        self.student.district = "mysuru"
        self.student.save()

        result = evaluate_eligibility(self.scholarship, self.student)
        self.assertEqual(result["criteria"]["district"]["status"], "passed")

    def test_course_requirement_passes(self):
        from scholarships.models import Course

        course = Course.objects.create(code="BE_BTECH", name="Engineering")
        self.scholarship.course.add(course)
        self.student.course = "BE_BTECH"
        self.student.save()

        result = evaluate_eligibility(self.scholarship, self.student)
        self.assertEqual(result["criteria"]["course"]["status"], "passed")

    def test_branch_requirement_passes(self):
        from scholarships.models import Branch

        branch = Branch.objects.create(code="CSE", name="Computer Science")
        self.scholarship.branch.add(branch)
        self.student.branch = "CSE"
        self.student.save()

        result = evaluate_eligibility(self.scholarship, self.student)
        self.assertEqual(result["criteria"]["branch"]["status"], "passed")

    def test_year_of_study_requirement_passes(self):
        self.scholarship.year_of_study = "3"
        self.scholarship.save()
        self.student.year_of_study = 3
        self.student.save()

        result = evaluate_eligibility(self.scholarship, self.student)
        self.assertEqual(result["criteria"]["year_of_study"]["status"], "passed")

    def test_postgraduate_requirement_passes(self):
        self.scholarship.year_of_study = "postgraduate"
        self.scholarship.save()
        self.student.course = "MCA"
        self.student.save()

        result = evaluate_eligibility(self.scholarship, self.student)
        self.assertEqual(result["criteria"]["year_of_study"]["status"], "passed")

    def test_gender_requirement_passes(self):
        self.scholarship.gender = "female"
        self.scholarship.save()
        self.student.gender = "FEMALE"
        self.student.save()

        result = evaluate_eligibility(self.scholarship, self.student)
        self.assertEqual(result["criteria"]["gender"]["status"], "passed")

    def test_pwd_requirement_passes(self):
        self.scholarship.pwd = True
        self.scholarship.save()
        self.student.pwd = True
        self.student.save()

        result = evaluate_eligibility(self.scholarship, self.student)
        self.assertEqual(result["criteria"]["pwd"]["status"], "passed")

    def test_minority_requirement_passes(self):
        self.scholarship.minority = True
        self.scholarship.save()
        self.student.minority = True
        self.student.save()

        result = evaluate_eligibility(self.scholarship, self.student)
        self.assertEqual(result["criteria"]["minority"]["status"], "passed")

    def test_missing_cgpa_returns_unknown(self):
        self.scholarship.minimum_cgpa = Decimal("7.00")
        self.scholarship.save()
        self.student.cgpa = None
        self.student.save()

        result = evaluate_eligibility(self.scholarship, self.student)
        self.assertEqual(result["criteria"]["cgpa"]["status"], "unknown")
        self.assertEqual(result["overall_status"], "incomplete")

    def test_missing_income_returns_unknown(self):
        self.scholarship.maximum_family_income = Decimal("250000")
        self.scholarship.save()
        self.student.family_income = None
        self.student.save()

        result = evaluate_eligibility(self.scholarship, self.student)
        self.assertEqual(result["criteria"]["family_income"]["status"], "unknown")
        self.assertEqual(result["overall_status"], "incomplete")

    def test_missing_gender_returns_unknown(self):
        self.scholarship.gender = "female"
        self.scholarship.save()
        self.student.gender = ""
        self.student.save()

        result = evaluate_eligibility(self.scholarship, self.student)
        self.assertEqual(result["criteria"]["gender"]["status"], "unknown")
        self.assertEqual(result["overall_status"], "incomplete")

    def test_missing_district_returns_unknown(self):
        from scholarships.models import District

        district = District.objects.create(code="MYSURU", name="Mysuru")
        self.scholarship.district.add(district)
        self.student.district = ""
        self.student.save()

        result = evaluate_eligibility(self.scholarship, self.student)
        self.assertEqual(result["criteria"]["district"]["status"], "unknown")
        self.assertEqual(result["overall_status"], "incomplete")

    def test_one_failed_requirement_makes_student_ineligible(self):
        self.scholarship.maximum_family_income = 200000
        self.scholarship.save()

        self.student.family_income = 300000
        self.student.save()

        result = evaluate_eligibility(
            self.scholarship,
            self.student,
        )

        self.assertEqual(result["overall_status"], "ineligible")
    def test_missing_required_info_returns_incomplete(self):
        self.scholarship.minimum_cgpa = Decimal("7.00")
        self.scholarship.save()

        self.student.cgpa = None
        self.student.save()

        result = evaluate_eligibility(
            self.scholarship,
            self.student,
        )

        self.assertEqual(result["criteria"]["cgpa"]["status"], "unknown")
        self.assertEqual(result["overall_status"], "incomplete")

    def test_age_requirement_fails(self):
        today = date.today()
        self.student.date_of_birth = date(
            today.year - 16,
            today.month,
            today.day,
        )
        self.student.save()
        self.scholarship.minimum_age = 18
        self.scholarship.save()

        result = evaluate_eligibility(self.scholarship, self.student)

        self.assertEqual(result["criteria"]["age"]["status"], "failed")

    def test_missing_age_returns_unknown(self):
        self.scholarship.minimum_age = 18
        self.scholarship.save()

        result = evaluate_eligibility(self.scholarship, self.student)

        self.assertEqual(result["criteria"]["age"]["status"], "unknown")

    def test_missing_category_returns_unknown(self):
        self.scholarship.category.add(
            Category.objects.create(code="OBC", name="Other Backward Classes")
        )

        result = evaluate_eligibility(self.scholarship, self.student)

        self.assertEqual(result["criteria"]["category"]["status"], "unknown")

    def test_missing_state_returns_unknown(self):
        self.scholarship.state.add(
            State.objects.create(code="KARNATAKA", name="Karnataka")
        )

        result = evaluate_eligibility(self.scholarship, self.student)

        self.assertEqual(result["criteria"]["state"]["status"], "unknown")

    def test_state_requirement_fails(self):
        self.scholarship.state.add(
            State.objects.create(code="KARNATAKA", name="Karnataka")
        )
        self.student.state = "TAMIL_NADU"
        self.student.save()

        result = evaluate_eligibility(self.scholarship, self.student)

        self.assertEqual(result["criteria"]["state"]["status"], "failed")

    def test_missing_course_returns_unknown(self):
        self.scholarship.course.add(
            Course.objects.create(code="BE_BTECH", name="Engineering")
        )

        result = evaluate_eligibility(self.scholarship, self.student)

        self.assertEqual(result["criteria"]["course"]["status"], "unknown")

    def test_course_requirement_fails(self):
        self.scholarship.course.add(
            Course.objects.create(code="BE_BTECH", name="Engineering")
        )
        self.student.course = "BSC"
        self.student.save()

        result = evaluate_eligibility(self.scholarship, self.student)

        self.assertEqual(result["criteria"]["course"]["status"], "failed")

    def test_missing_branch_returns_unknown(self):
        self.scholarship.branch.add(
            Branch.objects.create(code="CSE", name="Computer Science")
        )

        result = evaluate_eligibility(self.scholarship, self.student)

        self.assertEqual(result["criteria"]["branch"]["status"], "unknown")

    def test_branch_requirement_fails(self):
        self.scholarship.branch.add(
            Branch.objects.create(code="CSE", name="Computer Science")
        )
        self.student.branch = "ECE"
        self.student.save()

        result = evaluate_eligibility(self.scholarship, self.student)

        self.assertEqual(result["criteria"]["branch"]["status"], "failed")

    def test_year_of_study_requirement_fails(self):
        self.scholarship.year_of_study = "3"
        self.scholarship.save()
        self.student.year_of_study = 2
        self.student.save()

        result = evaluate_eligibility(self.scholarship, self.student)

        self.assertEqual(
            result["criteria"]["year_of_study"]["status"],
            "failed",
        )

    def test_missing_year_of_study_returns_unknown(self):
        self.scholarship.year_of_study = "3"
        self.scholarship.save()

        result = evaluate_eligibility(self.scholarship, self.student)

        self.assertEqual(
            result["criteria"]["year_of_study"]["status"],
            "unknown",
        )

    def test_postgraduate_requirement_without_course_returns_unknown(self):
        self.scholarship.year_of_study = "postgraduate"
        self.scholarship.save()

        result = evaluate_eligibility(self.scholarship, self.student)

        self.assertEqual(
            result["criteria"]["year_of_study"]["status"],
            "unknown",
        )

    def test_pwd_requirement_fails(self):
        self.scholarship.pwd = True
        self.scholarship.save()
        self.student.pwd = False
        self.student.save()

        result = evaluate_eligibility(self.scholarship, self.student)

        self.assertEqual(result["criteria"]["pwd"]["status"], "failed")

    def test_missing_pwd_returns_unknown(self):
        self.scholarship.pwd = True
        self.scholarship.save()

        result = evaluate_eligibility(self.scholarship, self.student)

        self.assertEqual(result["criteria"]["pwd"]["status"], "unknown")

    def test_minority_requirement_fails(self):
        self.scholarship.minority = True
        self.scholarship.save()
        self.student.minority = False
        self.student.save()

        result = evaluate_eligibility(self.scholarship, self.student)

        self.assertEqual(result["criteria"]["minority"]["status"], "failed")

    def test_missing_minority_returns_unknown(self):
        self.scholarship.minority = True
        self.scholarship.save()

        result = evaluate_eligibility(self.scholarship, self.student)

        self.assertEqual(result["criteria"]["minority"]["status"], "unknown")


class ScholarshipEligibilityAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="eligibility_api_test",
            password="StrongTestPass!2026",
        )
        self.student = StudentProfile.objects.create(
            user=self.user,
            full_name="API Test Student",
            percentage=Decimal("85.00"),
        )
        self.scholarship = Scholarship.objects.create(
            name="API Test Scholarship",
            provider="Test Provider",
            description="Eligibility API integration test",
            amount=Decimal("5000.00"),
            deadline=date(2027, 12, 31),
            status=Scholarship.Status.ACTIVE,
            minimum_percentage=Decimal("75.00"),
        )
        self.url = reverse(
            "scholarship-eligibility",
            kwargs={"scholarship_id": self.scholarship.id},
        )
        self.client.force_authenticate(user=self.user)

    def test_fully_eligible_student_receives_criterion_results(self):
        today = date.today()
        self.student.date_of_birth = date(
            today.year - 20,
            today.month,
            today.day,
        )
        self.student.gender = "FEMALE"
        self.student.state = "KARNATAKA"
        self.student.district = "MYSURU"
        self.student.category = "OBC"
        self.student.course = "BE_BTECH"
        self.student.branch = "CSE"
        self.student.year_of_study = 3
        self.student.cgpa = Decimal("8.50")
        self.student.family_income = Decimal("200000.00")
        self.student.pwd = True
        self.student.minority = True
        self.student.save()

        self.scholarship.minimum_cgpa = Decimal("7.00")
        self.scholarship.maximum_family_income = Decimal("250000.00")
        self.scholarship.minimum_age = 18
        self.scholarship.maximum_age = 25
        self.scholarship.gender = "female"
        self.scholarship.year_of_study = "3"
        self.scholarship.pwd = True
        self.scholarship.minority = True
        self.scholarship.save()
        self.scholarship.category.add(
            Category.objects.create(code="OBC", name="Other Backward Classes")
        )
        self.scholarship.state.add(
            State.objects.create(code="KARNATAKA", name="Karnataka")
        )
        self.scholarship.district.add(
            District.objects.create(code="MYSURU", name="Mysuru")
        )
        self.scholarship.course.add(
            Course.objects.create(code="BE_BTECH", name="Engineering")
        )
        self.scholarship.branch.add(
            Branch.objects.create(code="CSE", name="Computer Science")
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "scholarship_id": self.scholarship.id,
                "scholarship_name": self.scholarship.name,
                "overall_status": "eligible",
                "criteria": {
                    "percentage": {
                        "status": "passed",
                        "reason": "Required: 75.00%, student has: 85.00%.",
                    },
                    "cgpa": {
                        "status": "passed",
                        "reason": "Required: 7.00, student has: 8.50.",
                    },
                    "family_income": {
                        "status": "passed",
                        "reason": (
                            "Maximum allowed: ₹250000.00, student income: "
                            "₹200000.00."
                        ),
                    },
                    "age": {
                        "status": "passed",
                        "reason": "Student age: 20; age requirements satisfied.",
                    },
                    "gender": {
                        "status": "passed",
                        "reason": "Required gender: female.",
                    },
                    "category": {
                        "status": "passed",
                        "reason": "Student category OBC is accepted.",
                    },
                    "state": {
                        "status": "passed",
                        "reason": "Student state KARNATAKA is accepted.",
                    },
                    "district": {
                        "status": "passed",
                        "reason": "Student district MYSURU is accepted.",
                    },
                    "course": {
                        "status": "passed",
                        "reason": "Student course BE_BTECH is accepted.",
                    },
                    "branch": {
                        "status": "passed",
                        "reason": "Student branch CSE is accepted.",
                    },
                    "year_of_study": {
                        "status": "passed",
                        "reason": "Student is in year 3, as required.",
                    },
                    "pwd": {
                        "status": "passed",
                        "reason": (
                            "Student PwD status matches the scholarship "
                            "requirement."
                        ),
                    },
                    "minority": {
                        "status": "passed",
                        "reason": (
                            "Student minority status matches the scholarship "
                            "requirement."
                        ),
                    },
                },
            },
        )

    def test_student_failing_a_criterion_is_ineligible(self):
        self.scholarship.minimum_percentage = Decimal("90.00")
        self.scholarship.save()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["overall_status"], "ineligible")
        self.assertEqual(
            response.data["criteria"]["percentage"]["status"],
            "failed",
        )

    def test_missing_required_profile_information_is_incomplete(self):
        self.scholarship.minimum_cgpa = Decimal("7.00")
        self.scholarship.save()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["overall_status"], "incomplete")
        self.assertEqual(
            response.data["criteria"]["cgpa"]["status"],
            "unknown",
        )

    def test_unspecified_criteria_are_not_applicable(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["criteria"]["percentage"]["status"],
            "passed",
        )
        self.assertEqual(
            response.data["criteria"]["cgpa"]["status"],
            "not_applicable",
        )
        self.assertEqual(
            response.data["criteria"]["age"]["status"],
            "not_applicable",
        )
        self.assertEqual(response.data["overall_status"], "eligible")

    def test_invalid_scholarship_id_returns_not_found(self):
        response = self.client.get(
            reverse(
                "scholarship-eligibility",
                kwargs={"scholarship_id": 0},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data,
            {"detail": "Active scholarship not found."},
        )

    def test_unauthenticated_request_is_unauthorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_eligibility_uses_authenticated_students_profile(self):
        other_user = User.objects.create_user(
            username="other_eligibility_api_test",
            password="StrongTestPass!2026",
        )
        StudentProfile.objects.create(
            user=other_user,
            full_name="Other Student",
            percentage=Decimal("20.00"),
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["criteria"]["percentage"]["status"],
            "passed",
        )
        self.assertEqual(response.data["overall_status"], "eligible")
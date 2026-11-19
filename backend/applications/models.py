
from django.db import models
from django.contrib.auth.models import User
from django.db.models import UniqueConstraint

from scholarships.models import Scholarship


class Application(models.Model):

    class Status(models.TextChoices):
        NOT_APPLIED = "NOT_APPLIED", "Not Applied"
        INTERESTED = "INTERESTED", "Interested"
        APPLIED = "APPLIED", "Applied"
        UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    scholarship = models.ForeignKey(
        Scholarship,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NOT_APPLIED
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            UniqueConstraint(
                fields=["student", "scholarship"],
                name="unique_student_scholarship_application"
            )
        ]

    def __str__(self):
        return f"{self.student.username} - {self.scholarship.name}"

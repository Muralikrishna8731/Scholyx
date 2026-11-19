from django import template

from accounts.models import StudentProfile
from applications.models import Application
from scholarships.models import Scholarship


register = template.Library()


@register.inclusion_tag("admin/platform_stats.html")
def platform_stats():
    student_count = StudentProfile.objects.count()
    scholarships = Scholarship.objects
    applications = Application.objects

    return {
        "student_count": student_count,
        "scholarship_count": scholarships.count(),
        "scholarship_status_counts": [
            {
                "label": label,
                "count": scholarships.filter(status=status).count(),
            }
            for status, label in Scholarship.Status.choices
        ],
        "application_count": applications.count(),
        "application_status_counts": [
            {
                "label": label,
                "count": applications.filter(status=status).count(),
            }
            for status, label in Application.Status.choices
        ],
    }

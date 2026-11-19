from django.contrib import admin

from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "scholarship",
        "status",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "created_at", "updated_at")
    search_fields = (
        "student__username",
        "student__email",
        "student__student_profile__full_name",
        "scholarship__name",
        "scholarship__provider",
        "notes",
    )
    autocomplete_fields = ("student", "scholarship")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html, format_html_join

from applications.models import Application
from .models import StudentProfile


class ApplicationInline(admin.TabularInline):
    model = Application
    fk_name = "student"
    fields = ("scholarship", "status", "notes", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    extra = 0
    show_change_link = True


class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    extra = 0
    max_num = 1
    fields = (
        "full_name",
        "date_of_birth",
        "gender",
        "state",
        "district",
        "category",
        "course",
        "branch",
        "year_of_study",
        "college",
        "percentage",
        "cgpa",
        "family_income",
        "pwd",
        "minority",
    )


class StudentAccountStatusFilter(admin.SimpleListFilter):
    title = "account status"
    parameter_name = "account_status"

    def lookups(self, request, model_admin):
        return (
            ("active", "Active"),
            ("inactive", "Inactive"),
        )

    def queryset(self, request, queryset):
        if self.value() == "active":
            return queryset.filter(user__is_active=True)
        if self.value() == "inactive":
            return queryset.filter(user__is_active=False)
        return queryset


class UserAdmin(DjangoUserAdmin):
    inlines = (StudentProfileInline, ApplicationInline)
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "get_username",
        "get_email",
        "course",
        "year_of_study",
        "college",
        "state",
        "get_is_active",
    )
    list_filter = (
        StudentAccountStatusFilter,
        "gender",
        "state",
        "category",
        "course",
        "branch",
        "year_of_study",
        "pwd",
        "minority",
    )
    search_fields = (
        "full_name",
        "user__username",
        "user__email",
        "college",
        "district",
    )
    readonly_fields = ("get_application_count", "get_application_history")
    fieldsets = (
        ("Account", {
            "fields": (
                "user",
                "get_application_count",
                "get_application_history",
            )
        }),
        ("Personal information", {
            "fields": (
                "full_name",
                "date_of_birth",
                "gender",
                "state",
                "district",
                "category",
            )
        }),
        ("Education", {
            "fields": (
                "course",
                "branch",
                "year_of_study",
                "college",
                "percentage",
                "cgpa",
            )
        }),
        ("Eligibility", {
            "fields": (
                "family_income",
                "pwd",
                "minority",
            )
        }),
    )

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = "Username"
    get_username.admin_order_field = "user__username"

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = "Email"
    get_email.admin_order_field = "user__email"

    def get_is_active(self, obj):
        return obj.user.is_active
    get_is_active.short_description = "Active"
    get_is_active.boolean = True
    get_is_active.admin_order_field = "user__is_active"

    def get_application_count(self, obj):
        return obj.user.applications.count()
    get_application_count.short_description = "Applications"

    def get_application_history(self, obj):
        applications = obj.user.applications.select_related("scholarship")
        if not applications.exists():
            return "No applications"

        rows = format_html_join(
            "",
            '<tr><td><a href="{}">{}</a></td><td>{}</td><td>{}</td></tr>',
            (
                (
                    reverse(
                        "admin:applications_application_change",
                        args=(application.pk,),
                    ),
                    application.scholarship.name,
                    application.get_status_display(),
                    application.updated_at,
                )
                for application in applications
            ),
        )
        return format_html(
            '<table><thead><tr><th>Scholarship</th>'
            "<th>Status</th><th>Updated</th></tr></thead><tbody>{}</tbody></table>",
            rows,
        )
    get_application_history.short_description = "Application history"


# Replace Django's default UserAdmin so student profiles and applications
# appear together in one account-management workflow.
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

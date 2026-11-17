from django.contrib import admin
from .models import (
	Branch,
	Category,
	Course,
	District,
	RequiredDocument,
	Scholarship,
	State,
)


class RequiredDocumentInline(admin.TabularInline):
	model = RequiredDocument
	extra = 0


@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
	list_display = ("name", "provider", "amount", "deadline", "status")
	list_filter = ("status", "gender", "year_of_study", "pwd", "minority")
	search_fields = ("name", "provider")
	filter_horizontal = ("category", "state", "district", "course", "branch")
	date_hierarchy = "deadline"
	inlines = (RequiredDocumentInline,)


@admin.register(RequiredDocument)
class RequiredDocumentAdmin(admin.ModelAdmin):
	list_display = ("name", "scholarship", "is_mandatory")
	list_filter = ("is_mandatory",)
	search_fields = ("name", "scholarship__name")


@admin.register(Branch, Category, Course, District, State)
class EligibilityOptionAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")
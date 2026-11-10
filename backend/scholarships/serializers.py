
from decimal import Decimal

from django.db.models import Q
from rest_framework import serializers

from .models import (
    Branch,
    Category,
    Course,
    District,
    RequiredDocument,
    Scholarship,
    State,
)


class RequiredDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequiredDocument
        fields = [
            "id",
            "name",
            "description",
            "is_mandatory",
        ]


class ScholarshipSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(many=True, read_only=True)
    state = serializers.StringRelatedField(many=True, read_only=True)
    district = serializers.StringRelatedField(many=True, read_only=True)
    course = serializers.StringRelatedField(many=True, read_only=True)
    branch = serializers.StringRelatedField(many=True, read_only=True)

    required_documents = RequiredDocumentSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Scholarship
        fields = [
            "id",
            "name",
            "provider",
            "description",
            "amount",
            "deadline",
            "official_website",
            "application_url",
            "minimum_percentage",
            "minimum_cgpa",
            "maximum_family_income",
            "minimum_age",
            "maximum_age",
            "gender",
            "category",
            "state",
            "district",
            "course",
            "branch",
            "year_of_study",
            "pwd",
            "minority",
            "required_documents",
        ]


class ScholarshipQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=False)
    amount = serializers.DecimalField(
        required=False,
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )
    min_amount = serializers.DecimalField(
        required=False,
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0"),
    )
    deadline_before = serializers.DateField(required=False)
    course = serializers.CharField(required=False)
    branch = serializers.CharField(required=False)
    category = serializers.CharField(required=False)
    state = serializers.CharField(required=False)
    district = serializers.CharField(required=False)
    gender = serializers.ChoiceField(
        required=False,
        choices=Scholarship.Gender.choices,
    )
    year_of_study = serializers.ChoiceField(
        required=False,
        choices=Scholarship.YearOfStudy.choices,
    )

    option_models = {
        "course": Course,
        "branch": Branch,
        "category": Category,
        "state": State,
        "district": District,
    }

    def validate(self, attrs):
        for field_name, model in self.option_models.items():
            value = attrs.get(field_name)
            if value is None:
                continue

            if not model.objects.filter(
                Q(code__iexact=value) | Q(name__iexact=value)
            ).exists():
                raise serializers.ValidationError(
                    {field_name: "Select a valid option code or name."}
                )

        return attrs

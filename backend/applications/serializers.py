from rest_framework import serializers
from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Application
        fields = [
            "id",
            "scholarship",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_scholarship(self, value):
        request = self.context.get("request")

        if request and Application.objects.filter(
            student=request.user,
            scholarship=value
        ).exists():
            raise serializers.ValidationError(
                "You are already tracking this scholarship."
            )

        return value
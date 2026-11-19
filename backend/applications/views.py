from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Application
from .serializers import ApplicationSerializer


class ApplicationListCreateView(generics.ListCreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class ApplicationDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(student=self.request.user)
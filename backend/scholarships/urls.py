from django.urls import path

from .views import ScholarshipDetailView, ScholarshipListView


urlpatterns = [
    path(
        "scholarships/",
        ScholarshipListView.as_view(),
        name="scholarship-list",
    ),
    path(
        "scholarships/<int:pk>/",
        ScholarshipDetailView.as_view(),
        name="scholarship-detail",
    ),
]

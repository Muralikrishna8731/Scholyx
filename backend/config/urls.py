
"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import include, path
from accounts.views import my_profile


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/", include("scholarships.urls")),
    path("api/", include("eligibility.urls")),
    path("api/profile/me/", my_profile, name="my-profile"),
]

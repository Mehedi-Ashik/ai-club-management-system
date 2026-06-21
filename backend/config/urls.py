from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include("core.urls")),
    path("accounts/", include("accounts.urls")),
    path("members/", include("members.urls")),
    path("events/", include("events.urls")),
    path("payments/", include("payments.urls")),
    path("attendance/", include("attendance.urls")),
    path("certificates/", include("certificates.urls")),
    path("blog/", include("blog.urls")),
    path("forum/", include("forum.urls")),
    path("notifications/", include("notifications.urls")),
    path("ai/", include("ai_features.urls")),
]

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # --- Django Admin ---
    path("admin/", admin.site.urls),

    # --- API Routes (Versioned) ---
    path("api/v1/", include("login.urls")),       # 🔑 Authentication & User Management
    path("api/v1/", include("attendance.urls")),  # 📊 Attendance & Role Dashboards
]

# --- Static & Media (Development only) ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


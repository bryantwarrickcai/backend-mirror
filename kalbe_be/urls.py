from django.contrib import admin
from django.urls import path, include
from authentication.views import protected_endpoint
from annotation.views_page import AnnotationTesterPage
from django.conf import settings
from django.conf.urls.static import static

# CSRF token endpoint (for SPA/Next.js to fetch a token)
from accounts.csrf import csrf as csrf_view

urlpatterns = [
    path("admin/", admin.site.urls),

    # CSRF endpoint used by the frontend: GET http://localhost:8000/api/csrf/
    path("api/csrf/", csrf_view),

    # Accounts app routes (OTP request/confirm/test live under /accounts/…)
    path("accounts/", include("accounts.urls")),
    path('auth/', include('authentication.urls')),
    path('api/protected-endpoint/', protected_endpoint),
    path('ocr/', include('ocr.urls')),
    path('annotation/test/', AnnotationTesterPage.as_view(), name='annotation-test'),
    path('', include('annotation.urls')),
    path('csv/', include('csv_export.urls')),
    path('save-to-database/', include('save_to_database.urls')),
    path('api/', include('activity_log.urls')),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from django.urls import path
from .views import ocr_test_page, health

app_name = "ocr"

urlpatterns = [
    path("health/", health, name="health"),
    path("", ocr_test_page, name="ocr_test_page"),
]

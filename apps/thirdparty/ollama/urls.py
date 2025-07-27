from django.urls import path

from apps.thirdparty.ollama import views

app_name = "ollama"

urlpatterns = [
    path("health/check", views.OllamaHealthCheckAPIView.as_view(), name="health_check"),
]

from django.urls import include, path


urlpatterns = [
    # Telegram webhook
    path("telegram/", include("apps.thirdparty.telegram.urls")),
    # Ollama API endpoints
    path("ollama/", include("apps.thirdparty.ollama.urls")),
]

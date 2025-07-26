from django.conf import settings
import requests


class OllamaService:
    """Service for interacting with Ollama API"""

    def __init__(self):
        self.base_url = settings.OLLAMA_CONFIG["BASE_URL"]
        self.default_model = settings.OLLAMA_CONFIG["DEFAULT_MODEL"]
        self.fallback_model = settings.OLLAMA_CONFIG["FALLBACK_MODEL"]
        self.timeout = settings.OLLAMA_CONFIG["TIMEOUT"]

    def health_check(self):
        """Check the health of the Ollama service."""
        if not self.base_url:
            return {"status": "unhealthy", "error": "Base URL is not configured"}
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as e:
            return {"status": "unhealthy", "error": str(e)}

        return {"status": "healthy", "base_url": self.base_url}

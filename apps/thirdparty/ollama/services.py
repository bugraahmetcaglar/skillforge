import logging
from typing import Any, Dict, List, Optional
import requests

from django.conf import settings


logger = logging.getLogger(__name__)


class OllamaService:
    """Service for interacting with Ollama API"""

    def __init__(self):
        self.base_url = settings.OLLAMA_CONFIG["BASE_URL"]
        self.default_model = settings.OLLAMA_CONFIG["DEFAULT_MODEL"]
        self.fallback_model = settings.OLLAMA_CONFIG["FALLBACK_MODEL"]
        self.timeout = settings.OLLAMA_CONFIG["TIMEOUT"]

    def health_check(self) -> Dict[str, Any]:
        """Check Ollama service health and return status matching serializer structure"""
        try:
            # Check if Ollama is running
            response = requests.get(f"{self.base_url}/api/tags", timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                available_models = [model["name"] for model in data.get("models", [])]

                # Determine service status based on model availability
                status = self._determine_status(available_models)

                return {
                    "status": status,
                    "ready_for_chat": self._is_ready_for_chat(available_models),
                    "available_models": available_models,
                    "default_model": self.default_model,
                    "fallback_model": self.fallback_model,
                }
            else:
                return {
                    "status": "unhealthy",
                    "ready_for_chat": False,
                    "default_model": self.default_model,
                    "fallback_model": self.fallback_model,
                    "error": f"HTTP {response.status_code}",
                }

        except requests.exceptions.ConnectionError:
            logger.error("Could not connect to Ollama service")
            return {
                "status": "unreachable",
                "ready_for_chat": False,
                "default_model": self.default_model,
                "fallback_model": self.fallback_model,
                "error": "Connection failed - service may be down",
            }

        except requests.exceptions.Timeout:
            logger.error("Ollama service timeout")
            return {
                "status": "timeout",
                "ready_for_chat": False,
                "default_model": self.default_model,
                "fallback_model": self.fallback_model,
                "error": f"Request timeout after {self.timeout} seconds",
            }

        except Exception as e:
            logger.exception(f"Ollama health check failed: {e}")
            return {
                "status": "error",
                "ready_for_chat": False,
                "default_model": self.default_model,
                "fallback_model": self.fallback_model,
                "error": f"Unexpected error: {str(e)}",
            }

    def _is_ready_for_chat(self, available_models: List[str]) -> bool:
        """Check if service is ready to handle chat requests"""
        return self.default_model in available_models or self.fallback_model in available_models

    def _get_error_message(self, status: str, available_models: List[str]) -> Optional[str]:
        """Generate appropriate error message based on status"""
        if status == "healthy":
            if self.default_model not in available_models:
                return f"Default model '{self.default_model}' unavailable, using fallback"
            return None

        elif status == "unhealthy":
            if not available_models:
                return "No models are available"
            else:
                return f"Required models not found. Available: {', '.join(available_models)}"

        # For other statuses (unreachable, timeout, error), error message is set in main method
        return None

    def _determine_status(self, available_models: List[str]) -> str:
        """Determine service status based on available models"""
        if not available_models:
            return "unhealthy"

        has_default = self.default_model in available_models
        has_fallback = self.fallback_model in available_models

        if has_default or has_fallback:
            return "healthy"
        else:
            return "unhealthy"

"""API for Bwee Home integration."""

from .api_client import ApiClient
from .api_models import Result

API = ApiClient()

__all__ = ["API", "ApiClient", "Result"]

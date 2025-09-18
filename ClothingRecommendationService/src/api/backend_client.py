from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel


class BackendConfig(BaseModel):
    """Configuration for backend base URL and paths."""
    base_url: str = "http://localhost:8090"
    weather_path: str = "/api/weather"
    clothing_path: str = "/api/clothing"
    places_path: str = "/api/places"


class BackendClient:
    """Simple HTTP client to interact with ClothingRecommendationService_backend."""

    def __init__(self, config: Optional[BackendConfig] = None) -> None:
        self.config = config or BackendConfig()
        self._client = httpx.Client(base_url=self.config.base_url, timeout=10)

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    # PUBLIC_INTERFACE
    def get_weather(self, city: str) -> Dict[str, Any]:
        """Fetch weather info for a city from backend."""
        resp = self._client.get(self.config.weather_path, params={"city": city})
        resp.raise_for_status()
        return resp.json()

    # PUBLIC_INTERFACE
    def get_clothing(self, city: str) -> List[Dict[str, Any]]:
        """Fetch clothing recommendations for a city from backend."""
        resp = self._client.get(self.config.clothing_path, params={"city": city})
        resp.raise_for_status()
        data = resp.json()
        # Accept either list or object with 'items'
        if isinstance(data, dict) and "items" in data and isinstance(data["items"], list):
            return data["items"]
        if isinstance(data, list):
            return data
        return []

    # PUBLIC_INTERFACE
    def get_places(self, city: str) -> List[Dict[str, Any]]:
        """Fetch popular places for a city from backend."""
        resp = self._client.get(self.config.places_path, params={"city": city})
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict) and "places" in data and isinstance(data["places"], list):
            return data["places"]
        if isinstance(data, list):
            return data
        return []

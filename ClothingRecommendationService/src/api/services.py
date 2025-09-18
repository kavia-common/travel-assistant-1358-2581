from typing import List

from .backend_client import BackendClient
from .models import ClothingRecommendation, PlaceInfo, TravelAdvice, WeatherInfo


def _synthesize_tips(weather: WeatherInfo, clothing: List[ClothingRecommendation], places: List[PlaceInfo]) -> List[str]:
    """Create simple human tips based on inputs."""
    tips: List[str] = []
    if weather.temperature_c <= 5:
        tips.append("It's quite cold; plan more indoor activities and wear thermal layers.")
    elif weather.temperature_c >= 30:
        tips.append("High temperatures expected; stay hydrated and avoid midday sun.")
    else:
        tips.append("Mild weather; flexible itinerary works well.")

    ws = weather.summary.lower()
    if "rain" in ws:
        tips.append("Carry a compact umbrella or waterproof jacket.")
    if "wind" in ws or "breezy" in ws:
        tips.append("A windbreaker may be useful due to breezy conditions.")

    if places:
        tips.append("Purchase tickets online for popular attractions to skip lines.")
    if any("walking" in (rec.reason or "").lower() for rec in clothing):
        tips.append("Comfortable walking shoes are recommended.")
    return tips


# PUBLIC_INTERFACE
def build_travel_advice(city: str, client: BackendClient) -> TravelAdvice:
    """Fetch backend data and compose integrated travel advice for a city."""
    weather_json = client.get_weather(city)
    clothing_json = client.get_clothing(city)
    places_json = client.get_places(city)

    # Normalize into models
    weather = WeatherInfo(
        summary=str(weather_json.get("summary") or weather_json.get("description") or "Unknown"),
        temperature_c=float(weather_json.get("temperature_c")
                            or weather_json.get("temp_c")
                            or weather_json.get("temperature", 0.0)),
        feels_like_c=(float(weather_json["feels_like_c"]) if "feels_like_c" in weather_json else None),
        humidity_pct=(float(weather_json["humidity_pct"]) if "humidity_pct" in weather_json else None),
        wind_kph=(float(weather_json["wind_kph"]) if "wind_kph" in weather_json else None),
    )

    clothing = [
        ClothingRecommendation(
            item=str(item.get("item") or item.get("name") or "Unknown"),
            reason=(item.get("reason") or item.get("notes")),
        )
        for item in clothing_json
        if isinstance(item, dict)
    ]

    places = [
        PlaceInfo(
            name=str(p.get("name") or p.get("title") or "Unknown"),
            category=p.get("category"),
            description=p.get("description"),
            url=p.get("url") or p.get("link"),
        )
        for p in places_json
        if isinstance(p, dict)
    ]

    tips = _synthesize_tips(weather, clothing, places)

    return TravelAdvice(city=city, weather=weather, clothing=clothing, places=places, tips=tips)

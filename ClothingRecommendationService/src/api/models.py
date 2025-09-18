from typing import List, Optional

from pydantic import BaseModel, Field, constr


# PUBLIC_INTERFACE
class CityQuery(BaseModel):
    """Request model for querying recommendations by city."""
    city: constr(strip_whitespace=True, min_length=1) = Field(..., description="Name of the city to fetch travel advice for.")


class WeatherInfo(BaseModel):
    """Weather information returned by backend."""
    summary: str = Field(..., description="Short description of the weather (e.g., 'Sunny').")
    temperature_c: float = Field(..., description="Current temperature in Celsius.")
    feels_like_c: Optional[float] = Field(None, description="Feels like temperature in Celsius.")
    humidity_pct: Optional[float] = Field(None, description="Humidity percentage.")
    wind_kph: Optional[float] = Field(None, description="Wind speed in KPH.")


class ClothingRecommendation(BaseModel):
    """Clothing recommendation item."""
    item: str = Field(..., description="Name of the clothing item.")
    reason: Optional[str] = Field(None, description="Reason for the recommendation.")


class PlaceInfo(BaseModel):
    """Popular place to visit."""
    name: str = Field(..., description="Place name.")
    category: Optional[str] = Field(None, description="Type/category of the place (e.g., 'Museum').")
    description: Optional[str] = Field(None, description="Short description.")
    url: Optional[str] = Field(None, description="Reference URL.")


class TravelAdvice(BaseModel):
    """Aggregated travel advice for a city."""
    city: str = Field(..., description="City the advice pertains to.")
    weather: WeatherInfo = Field(..., description="Current weather details.")
    clothing: List[ClothingRecommendation] = Field(..., description="List of clothing recommendations.")
    places: List[PlaceInfo] = Field(..., description="Popular places to visit.")
    tips: Optional[List[str]] = Field(default=None, description="Additional travel tips synthesized from data.")

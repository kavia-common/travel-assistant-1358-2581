# ClothingRecommendationService Frontend

A FastAPI frontend that accepts a city and provides integrated travel advice by querying the ClothingRecommendationService_backend for:
- Current weather
- Clothing recommendations
- Popular places to visit

Technology: FastAPI

Assumptions:
- The backend is reachable at http://localhost:8090
- No environment variables are required for this step

## Run

Install dependencies and start the app:

```bash
pip install -r requirements.txt
uvicorn src.api.main:app --host 0.0.0.0 --port 8080 --reload
```

The frontend assumes the backend exposes:
- GET /api/weather?city=City
- GET /api/clothing?city=City
- GET /api/places?city=City

## Endpoints

- GET `/` — health check
- POST `/api/travel-advice` — body: `{ "city": "Paris" }` — returns aggregated advice (JSON)
- GET `/api/travel-advice?city=Paris` — query param variant
- GET `/demo` — interactive HTML demo page (renders weather, clothing, places, tips)

OpenAPI docs at:
- `/docs` (Swagger UI)
- `/redoc` (ReDoc)

### API Usage

- POST /api/travel-advice

Request:
```json
{ "city": "Paris" }
```

Response (example):
```json
{
  "city": "Paris",
  "weather": { "summary": "Sunny", "temperature_c": 21.5, "feels_like_c": 22, "humidity_pct": 45, "wind_kph": 12 },
  "clothing": [ { "item": "Light jacket", "reason": "Cool mornings" } ],
  "places": [ { "name": "Louvre Museum", "category": "Museum", "description": "World's largest art museum", "url": "https://www.louvre.fr" } ],
  "tips": [ "Mild weather; flexible itinerary works well." ]
}
```

Errors:
- 400 — Input validation error (e.g., empty city)
- 502 — Backend service error (backend unreachable or returned error)

## Development Notes

- App lifecycle creates a shared httpx Client for backend calls and closes it on shutdown.
- CORS is wide-open for demo convenience; tighten in production.
- `/demo` page provides a quick, no-dependency test UI.

### Lint

This repository includes flake8 configuration in `.flake8`. To lint locally:

```bash
# If using a virtualenv, ensure it's activated, then:
flake8
```

If flake8 is not available, install dev dependency:

```bash
pip install flake8
```

For CI environments where a pre-baked venv path is not available, you can run:

```bash
bash scripts/lint.sh
```

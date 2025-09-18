# ClothingRecommendationService Frontend

A FastAPI frontend that accepts a city and provides integrated travel advice by querying the ClothingRecommendationService_backend for:
- Current weather
- Clothing recommendations
- Popular places to visit

## Run

Install dependencies and start the app:

```bash
pip install -r requirements.txt
uvicorn src.api.main:app --host 0.0.0.0 --port 8080 --reload
```

The frontend assumes the backend is reachable at `http://localhost:8090` and exposes:
- GET /api/weather?city=City
- GET /api/clothing?city=City
- GET /api/places?city=City

## Endpoints

- GET `/` — health check
- POST `/api/travel-advice` — body: `{ "city": "Paris" }` — returns aggregated advice (JSON)
- GET `/api/travel-advice?city=Paris` — query param variant
- GET `/demo` — minimal HTML demo page

OpenAPI docs at `/docs` and `/redoc`.

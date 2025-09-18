from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import ValidationError

from .backend_client import BackendClient, BackendConfig
from .models import CityQuery, TravelAdvice
from .services import build_travel_advice


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup/shutdown resources like HTTP clients."""
    client = BackendClient(BackendConfig())
    app.state.backend_client = client
    try:
        yield
    finally:
        client.close()


app = FastAPI(
    title="ClothingRecommendationService Frontend",
    description="FastAPI frontend that accepts a city and returns integrated travel advice "
                "by querying the ClothingRecommendationService_backend for weather, clothing, and places.",
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "health", "description": "Health and status endpoints."},
        {"name": "advice", "description": "Travel advice endpoints."},
        {"name": "docs", "description": "Documentation helper endpoints."},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Demo-friendly: allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_backend_client() -> BackendClient:
    """Dependency provider for the backend client."""
    client: Optional[BackendClient] = getattr(app.state, "backend_client", None)
    if client is None:
        # Fallback instantiation (shouldn't happen under normal lifespan handling)
        client = BackendClient(BackendConfig())
        app.state.backend_client = client
    return client


# PUBLIC_INTERFACE
@app.get("/", tags=["health"], summary="Health check", description="Simple health check endpoint.")
def health_check():
    """Return service health status."""
    return {"message": "Healthy"}


# PUBLIC_INTERFACE
@app.post(
    "/api/travel-advice",
    response_model=TravelAdvice,
    tags=["advice"],
    summary="Get integrated travel advice by city",
    description="Accepts a city name and returns integrated advice including weather, clothing recommendations, and popular places.",
    responses={
        200: {"description": "Aggregated travel advice."},
        400: {"description": "Invalid input."},
        502: {"description": "Backend service error."},
    },
)
def get_travel_advice(body: CityQuery, client: BackendClient = Depends(get_backend_client)) -> TravelAdvice:
    """Endpoint to fetch and compose travel advice for the specified city."""
    try:
        advice = build_travel_advice(body.city, client)
        return advice
    except ValidationError as ve:
        # Pydantic validation issues within service
        raise HTTPException(status_code=400, detail=str(ve)) from ve
    except Exception as ex:
        # Proxy generic backend errors as Bad Gateway
        raise HTTPException(status_code=502, detail=f"Backend error: {str(ex)}") from ex


# PUBLIC_INTERFACE
@app.get(
    "/api/travel-advice",
    response_model=TravelAdvice,
    tags=["advice"],
    summary="Get integrated travel advice (query param)",
    description="Accepts a city as a query parameter and returns integrated travel advice.",
)
def get_travel_advice_q(
    city: str = Query(..., min_length=1, description="City name."),
    client: BackendClient = Depends(get_backend_client),
) -> TravelAdvice:
    """Query-param variant of the travel advice endpoint."""
    try:
        advice = build_travel_advice(city, client)
        return advice
    except ValidationError as ve:
        raise HTTPException(status_code=400, detail=str(ve)) from ve
    except Exception as ex:
        raise HTTPException(status_code=502, detail=f"Backend error: {str(ex)}") from ex


# PUBLIC_INTERFACE
@app.get(
    "/demo",
    tags=["advice"],
    response_class=HTMLResponse,
    summary="Simple HTML demo page",
    description="Basic demo page to try the travel advice endpoint from a browser.",
)
def demo() -> HTMLResponse:
    """Serve a minimal HTML page to test the service manually."""
    html = """
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>Clothing Recommendation Demo</title>
        <style>
          body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 2rem; }
          input, button { font-size: 1rem; padding: 0.5rem; }
          pre { background: #f6f8fa; padding: 1rem; border-radius: 8px; }
        </style>
      </head>
      <body>
        <h1>Clothing Recommendation Service</h1>
        <p>Try entering a city to get integrated travel advice (weather, clothing, places).</p>
        <input id="city" placeholder="e.g., Paris" />
        <button onclick="fetchAdvice()">Get Advice</button>
        <h3>Result</h3>
        <pre id="result"></pre>
        <script>
          async function fetchAdvice() {
            const city = document.getElementById('city').value;
            const res = await fetch(`/api/travel-advice?city=${encodeURIComponent(city)}`);
            const data = await res.json();
            document.getElementById('result').textContent = JSON.stringify(data, null, 2);
          }
        </script>
      </body>
    </html>
    """
    return HTMLResponse(html)


# PUBLIC_INTERFACE
@app.get(
    "/api/websocket-help",
    tags=["docs"],
    summary="WebSocket usage note",
    description="This service does not expose WebSocket endpoints. If real-time features are added in the future, "
                "they will be documented here with connection details.",
)
def websocket_help():
    """Provide WebSocket usage notes for API docs completeness."""
    return {"message": "No WebSocket endpoints available at this time."}

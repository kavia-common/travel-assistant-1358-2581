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
    description=(
        "FastAPI frontend that accepts a city and returns integrated travel advice "
        "by querying the ClothingRecommendationService_backend for weather, clothing, and places."
    ),
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
          .card { border: 1px solid #e1e4e8; border-radius: 8px; padding: 1rem; margin: 0.5rem 0; }
          .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }
          .muted { color: #586069; font-size: 0.9rem; }
        </style>
      </head>
      <body>
        <h1>Clothing Recommendation Service</h1>
        <p>Enter a city to get integrated travel advice (weather, clothing, places).</p>
        <input id="city" placeholder="e.g., Paris" />
        <button onclick="fetchAdvice()">Get Advice</button>
        <div id="error" style="color:#b00020;margin-top:8px;"></div>
        <div id="content" style="margin-top:16px; display:none;">
          <h2 id="title"></h2>
          <div class="card" id="weather"></div>
          <div class="card">
            <h3>Clothing Recommendations</h3>
            <ul id="clothing"></ul>
          </div>
          <div class="card">
            <h3>Popular Places</h3>
            <div id="places" class="grid"></div>
          </div>
          <div class="card">
            <h3>Tips</h3>
            <ul id="tips"></ul>
          </div>
          <p class="muted">Raw JSON below for debugging.</p>
          <pre id="result"></pre>
        </div>
        <script>
          function escapeHtml(s) {
            return s.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
          }
          async function fetchAdvice() {
            const city = document.getElementById('city').value.trim();
            const error = document.getElementById('error');
            const content = document.getElementById('content');
            error.textContent = '';
            content.style.display = 'none';
            if (!city) { error.textContent = 'Please enter a city.'; return; }
            try {
              const res = await fetch(`/api/travel-advice?city=${encodeURIComponent(city)}`);
              if (!res.ok) {
                const err = await res.json().catch(()=>({detail: res.statusText}));
                throw new Error(err.detail || `Request failed: ${res.status}`);
              }
              const data = await res.json();
              document.getElementById('result').textContent = JSON.stringify(data, null, 2);
              document.getElementById('title').textContent = `Travel Advice for ${data.city}`;
              const w = data.weather || {};
              document.getElementById('weather').innerHTML = `
                <strong>Weather:</strong> ${escapeHtml(String(w.summary||'Unknown'))}<br/>
                <strong>Temperature:</strong> ${escapeHtml(String(w.temperature_c))} °C
                ${w.feels_like_c != null ? `(feels like ${escapeHtml(String(w.feels_like_c))} °C)` : ''}<br/>
                ${w.humidity_pct != null ? `<strong>Humidity:</strong> ${escapeHtml(String(w.humidity_pct))}%<br/>` : ''}
                ${w.wind_kph != null ? `<strong>Wind:</strong> ${escapeHtml(String(w.wind_kph))} kph` : ''}
              `;
              const clothing = data.clothing || [];
              document.getElementById('clothing').innerHTML = clothing.map(c =>
                `<li>${escapeHtml(String(c.item))}${c.reason ? ` — ${escapeHtml(String(c.reason))}` : ''}</li>`
              ).join('') || '<li>No clothing recommendations.</li>';
              const places = data.places || [];
              document.getElementById('places').innerHTML = places.map(p => `
                <div class="card">
                  <strong>${escapeHtml(String(p.name))}</strong><br/>
                  ${p.category ? `<span class="muted">${escapeHtml(String(p.category))}</span><br/>` : ''}
                  ${p.description ? `<div>${escapeHtml(String(p.description))}</div>` : ''}
                  ${p.url ? `<a href="${escapeHtml(String(p.url))}" target="_blank">Learn more</a>` : ''}
                </div>`).join('') || '<div class="muted">No places found.</div>';
              const tips = data.tips || [];
              document.getElementById('tips').innerHTML = tips.map(t => `<li>${escapeHtml(String(t))}</li>`).join('') || '<li>No additional tips.</li>';
              content.style.display = '';
            } catch (e) {
              error.textContent = e.message || 'Unexpected error occurred.';
            }
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

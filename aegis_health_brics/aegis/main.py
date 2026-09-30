"""
AegisHealth BRICS - FastAPI Application Entrypoint.
Federated AI Platform for National-Scale Health Resource & Supply Chain Management.
Track 3: Smart Health & Supply Chain Resilience.
"""
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from aegis.api.routes import api_router
from aegis.config import PLATFORM_NAME, VERSION, THEME, TRACK

app = FastAPI(
    title=PLATFORM_NAME,
    version=VERSION,
    description=(
        f"Federated AI Platform for National-Scale Health Resource & Supply Chain Management. "
        f"Built for {TRACK} ({THEME}). Features real-time visibility into medicine stocks, "
        f"bed availability, and personnel attendance across Primary Health Centres (PHCs); "
        f"AI demand forecasting; automated cross-district resource redistribution; "
        f"and privacy-preserving federated predictive modelling across BRICS partner nations."
    ),
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router)

# Static files directory
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def serve_index():
    """Serves the main single-page command dashboard."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": f"Welcome to {PLATFORM_NAME} API. Access API docs at /docs"}

@app.get("/health")
def health_check():
    """Liveness probe."""
    return {"status": "HEALTHY", "platform": PLATFORM_NAME, "version": VERSION}

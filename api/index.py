from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Since Vercel Root Directory is set to "api",
# engine.py is in the same directory as this file.
from engine import DataEngine

app = FastAPI(
    title="ARGONAUT AI API",
    version="3.1.0",
    description="Conversational ARGO ocean-data exploration and visualization API.",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize data engine
engine = DataEngine()


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def root():
    return {
        "service": "ARGONAUT AI",
        "status": "online",
        "version": "3.1.0",
        "message": "Welcome to ARGONAUT AI API"
    }


@app.get("/api")
def api_root():
    return {
        "service": "ARGONAUT AI",
        "status": "online",
        "version": "3.1.0"
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "ARGONAUT AI",
        "version": "3.1.0"
    }


@app.get("/api/dashboard")
def dashboard():
    return engine.dashboard()


@app.post("/api/chat")
def chat(req: ChatRequest):
    if not req.message or not req.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message is required"
        )

    return engine.answer(req.message)


@app.get("/api/float/{wmo}")
def float_data(wmo: str):
    result = engine.float_data(wmo)

    if not result.get("rows"):
        raise HTTPException(
            status_code=404,
            detail=f"No data found for ARGO float {wmo}"
        )

    return result


@app.get("/api/float/{wmo}/plot")
def plot(wmo: str, plot_type: str = "temp_vs_depth"):
    return engine.plot(wmo, plot_type)


@app.get("/api/float/{wmo}/trajectory")
def trajectory(wmo: str):
    return engine.trajectory(wmo)


@app.get("/api/nearest")
def nearest(lat: float, lon: float):
    if not -90 <= lat <= 90:
        raise HTTPException(
            status_code=400,
            detail="Latitude must be between -90 and 90"
        )

    if not -180 <= lon <= 180:
        raise HTTPException(
            status_code=400,
            detail="Longitude must be between -180 and 180"
        )

    return {
        "latitude": lat,
        "longitude": lon,
        "floats": engine.nearest(lat, lon)
    }

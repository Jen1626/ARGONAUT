from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from api.engine import DataEngine

app = FastAPI(
    title="ARGONAUT AI API",
    version="3.1.0",
    description="Conversational ARGO ocean-data exploration and visualization API.",
)

# Same-origin Vercel deployment does not need CORS, but keeping permissive CORS
# makes the API easy to test from a separate local frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = DataEngine()


class ChatRequest(BaseModel):
    message: str


@app.get("/api")
def api_root():
    return {"service": "ARGONAUT AI", "status": "online", "version": "3.1.0"}


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "ARGONAUT AI", "version": "3.1.0"}


@app.get("/api/dashboard")
def dashboard():
    return engine.dashboard()


@app.post("/api/chat")
def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message is required")
    return engine.answer(req.message)


@app.get("/api/float/{wmo}")
def float_data(wmo: str):
    return engine.float_data(wmo)


@app.get("/api/float/{wmo}/plot")
def plot(wmo: str, plot_type: str = "temp_vs_depth"):
    return engine.plot(wmo, plot_type)


@app.get("/api/float/{wmo}/trajectory")
def trajectory(wmo: str):
    return engine.trajectory(wmo)


@app.get("/api/nearest")
def nearest(lat: float, lon: float):
    return {"latitude": lat, "longitude": lon, "floats": engine.nearest(lat, lon)}

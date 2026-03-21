"""
EspressoPi FastAPI Backend
Real-time espresso shot control, logging, and API.
"""
import logging
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from config import load_config, get_config
from database import init_database, get_database
from hardware.sensors import SensorReader
from hardware.gpio import GPIO
from controllers.shot_controller import ShotController
from models.profile import PROFILES


# ─── LOGGING ───
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ─── GLOBAL STATE ───
config = None
database = None
sensors = None
gpio = None
shot_controller = None


# ─── PYDANTIC MODELS ───
class ShotStartRequest(BaseModel):
    """Request to start a shot."""
    profile_name: str = "classic-9bar"
    notes: str = ""


class ShotStatsResponse(BaseModel):
    """Shot statistics response."""
    duration: float
    volume: float
    pressure_peak: float
    pressure_avg: float
    temperature_avg: float
    extraction_yield: float


class ShotResponse(BaseModel):
    """Full shot response."""
    id: str
    timestamp: str
    duration: float
    volume: float
    profile_name: str
    stats: ShotStatsResponse
    notes: str


class ProfileResponse(BaseModel):
    """Pressure profile response."""
    name: str
    description: str
    author: str
    points: list


class MachineStatusResponse(BaseModel):
    """Current machine state."""
    boiler_temp: float
    steam_pressure: float
    water_level: float
    state: str  # idle, running, paused


# ─── LIFESPAN ───
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    global config, database, sensors, gpio, shot_controller
    
    # Startup
    logger.info("Starting EspressoPi backend...")
    
    config = load_config("config.toml")
    database = init_database(config.database.get("path", "./data/shots.db"))
    sensors = SensorReader("ADS1256")
    gpio = GPIO(config.gpio)
    
    # Load default profile
    default_profile_name = config.profiles.get("default_profile", "classic-9bar")
    default_profile = PROFILES.get(default_profile_name)
    
    if not default_profile:
        logger.warning(f"Default profile not found: {default_profile_name}")
        default_profile = list(PROFILES.values())[0]
    
    shot_controller = ShotController(sensors, gpio, default_profile, config)
    
    logger.info("✅ Backend started successfully")
    logger.info(f"  Machine: {config.machine.get('name')}")
    logger.info(f"  Database: {config.database.get('path')}")
    logger.info(f"  API: http://0.0.0.0:{config.api.get('port', 8000)}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    if gpio:
        gpio.cleanup()
    if database:
        database.close()
    logger.info("✅ Shutdown complete")


# ─── FASTAPI APP ───
app = FastAPI(
    title="EspressoPi API",
    description="Real-time espresso machine controller",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.api.get("cors_origins", ["*"]) if config else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── API ENDPOINTS ───

@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": "EspressoPi API",
        "version": "0.1.0",
        "machine": config.machine.get("name"),
        "status": "ready",
    }


@app.get("/api/status")
async def get_status() -> MachineStatusResponse:
    """Get current machine status."""
    # Read live sensors
    pressure = sensors.read_pressure_brew()
    steam = sensors.read_pressure_steam()
    water = sensors.read_water_level()
    
    # Update database
    database.update_machine_state(
        boiler_temp=sensors.read_temperature().value,
        steam_pressure=steam.value,
        water_level=water.value,
    )
    
    return MachineStatusResponse(
        boiler_temp=sensors.read_temperature().value,
        steam_pressure=steam.value,
        water_level=water.value,
        state=shot_controller.state.value,
    )


@app.post("/api/shot/start")
async def start_shot(request: ShotStartRequest) -> dict:
    """Start a new shot with given profile."""
    # Get profile
    profile = PROFILES.get(request.profile_name)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile not found: {request.profile_name}")
    
    # Create new shot controller with this profile
    global shot_controller
    shot_controller = ShotController(sensors, gpio, profile, config)
    shot = shot_controller.start_shot()
    shot.notes = request.notes
    
    # Start update loop in background
    asyncio.create_task(_shot_update_loop())
    
    return {
        "id": shot.id,
        "profile": request.profile_name,
        "status": "started",
    }


@app.post("/api/shot/stop")
async def stop_shot() -> dict:
    """Stop the current shot."""
    if shot_controller.state.value != "running":
        raise HTTPException(status_code=400, detail="No shot in progress")
    
    shot = shot_controller.stop_shot()
    database.save_shot(shot)
    
    return {
        "id": shot.id,
        "duration": shot.duration,
        "volume": shot.volume,
        "status": "stopped",
    }


@app.get("/api/shot/{shot_id}")
async def get_shot(shot_id: str) -> dict:
    """Retrieve a specific shot."""
    shot_data = database.get_shot(shot_id)
    if not shot_data:
        raise HTTPException(status_code=404, detail=f"Shot not found: {shot_id}")
    return shot_data


@app.get("/api/shots")
async def list_shots(limit: int = 100, offset: int = 0) -> dict:
    """Get recent shots."""
    shots = database.get_shots(limit, offset)
    return {
        "shots": shots,
        "limit": limit,
        "offset": offset,
        "total": len(shots),
    }


@app.get("/api/profiles")
async def list_profiles() -> dict:
    """Get all available pressure profiles."""
    profiles = [p.to_dict() for p in PROFILES.values()]
    return {
        "profiles": profiles,
        "count": len(profiles),
    }


@app.get("/api/profiles/{name}")
async def get_profile(name: str) -> dict:
    """Get a specific profile."""
    profile = PROFILES.get(name)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile not found: {name}")
    return profile.to_dict()


@app.post("/api/settings/theme")
async def set_theme(theme_name: str) -> dict:
    """Apply a theme configuration."""
    # TODO: Load and apply theme
    return {"theme": theme_name, "status": "applied"}


# ─── MARKETPLACE ───

@app.get("/api/marketplace/profiles")
async def get_marketplace_profiles(limit: int = 50) -> dict:
    """Get available profiles from marketplace."""
    # TODO: Fetch from marketplace API
    # For now, return empty (stub)
    return {
        "profiles": [],
        "total": 0,
        "url": config.get("marketplace", "url"),
    }


@app.get("/api/marketplace/themes")
async def get_marketplace_themes(limit: int = 50) -> dict:
    """Get available themes from marketplace."""
    # TODO: Fetch from marketplace API
    return {
        "themes": [],
        "total": 0,
        "url": config.get("marketplace", "url"),
    }


@app.post("/api/marketplace/install/profile")
async def install_profile(name: str, config_json: dict) -> dict:
    """Install a profile from marketplace."""
    # TODO: Validate + install profile
    return {"profile": name, "status": "installed"}


@app.post("/api/marketplace/install/theme")
async def install_theme(name: str, config_json: dict) -> dict:
    """Install a theme from marketplace."""
    # TODO: Validate + install theme
    return {"theme": name, "status": "installed"}


@app.post("/api/marketplace/share")
async def share_to_marketplace(item_type: str, name: str, config_json: dict) -> dict:
    """Submit a profile/theme to marketplace (future)."""
    # TODO: Validate + submit to marketplace
    return {"item": name, "status": "submitted"}


# ─── WEBSOCKET ───

@app.websocket("/ws/live")
async def websocket_live(websocket: WebSocket):
    """WebSocket for real-time shot data during execution."""
    await websocket.accept()
    logger.info("WebSocket client connected")
    
    try:
        while True:
            # Send current state every 100ms
            if shot_controller.state.value == "running":
                state = shot_controller.get_current_state()
                await websocket.send_json(state)
            
            await asyncio.sleep(0.1)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        logger.info("WebSocket client disconnected")


# ─── BACKGROUND TASKS ───

async def _shot_update_loop():
    """Update shot state while running."""
    while shot_controller.state.value == "running":
        shot_controller.update()
        await asyncio.sleep(0.05)  # 20 Hz update rate


# ─── ERROR HANDLERS ───

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


if __name__ == "__main__":
    import uvicorn
    
    port = config.api.get("port", 8000) if config else 8000
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

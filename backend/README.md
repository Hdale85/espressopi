# EspressoPi Backend

Real-time espresso machine controller API built with FastAPI.

## Features

- **Config-driven GPIO** — All pins and settings in `config.toml`
- **Mock sensors** — Test without hardware
- **Pressure profiling** — Execute custom pressure curves
- **Shot logging** — SQLite database of every shot
- **RESTful API** — Full control via HTTP
- **WebSocket streaming** — Real-time live data during shots
- **Theme support** — Extensible UI customization

## Quick Start

### Install

```bash
cd backend
pip install -r requirements.txt
```

### Configure

Edit `config.toml` with your machine settings:

```toml
[machine]
name = "Wega IO 1GR"

[sensors]
pressure_brew_channel = 0
pressure_steam_channel = 1

[gpio]
pump_enable_pin = 23
group_solenoid_pin = 24
```

### Run (Mock Mode)

```bash
python main.py
```

API available at `http://localhost:8000`

API docs at `http://localhost:8000/docs`

## API Reference

### Status

```
GET /api/status
```

Returns current machine state (temperatures, pressures, water level).

### Start Shot

```
POST /api/shot/start
{
  "profile_name": "classic-9bar",
  "notes": "Single origin Ethiopian"
}
```

Starts a shot with the specified pressure profile.

### Stop Shot

```
POST /api/shot/stop
```

Stops the current shot and saves it.

### Get Shot

```
GET /api/shot/{shot_id}
```

Retrieve a completed shot with all data.

### List Shots

```
GET /api/shots?limit=100&offset=0
```

Get recent shots (paginated).

### List Profiles

```
GET /api/profiles
```

Get all available pressure profiles.

### Marketplace

```
GET /api/marketplace/profiles
GET /api/marketplace/themes
POST /api/marketplace/install/profile
POST /api/marketplace/install/theme
```

Browse and install profiles/themes from the marketplace.

Response format:

```json
{
  "profiles": [
    {
      "id": "espresso-bloom",
      "name": "Espresso Bloom",
      "description": "Extended pre-infusion...",
      "author": "@coffeegeek",
      "image_url": "https://cdn.espressopi.io/profiles/bloom.png",
      "ratings": 4.9,
      "installs": 324,
      "config": { /* profile JSON */ }
    }
  ]
}
```

**Image guidelines:**
- PNG or JPEG format
- Minimum 400×400px for clarity
- For profiles: graph screenshot or pressure curve visualization
- For themes: full UI screenshot showing the theme in action
- Keep file <1MB for fast loading

### Live Stream

```
ws://localhost:8000/ws/live
```

WebSocket connection for real-time shot data during execution.

Messages:

```json
{
  "state": "running",
  "elapsed": 15.3,
  "pressure_current": 9.1,
  "pressure_target": 9.0,
  "volume": 25.5,
  "temperature": 93.2,
  "shot_id": "abc123..."
}
```

## Architecture

```
main.py              # FastAPI app + routes
config.py            # Config loader
config.toml          # Machine configuration

models/
  shot.py           # Shot + ShotStats dataclasses
  profile.py        # Pressure profile + ProfilePoint

hardware/
  sensors.py        # Sensor readers (mock + real)
  gpio.py           # GPIO control (mock + real)

controllers/
  shot_controller.py # Shot execution logic

database/
  db.py             # SQLite helpers
  schema.sql        # Database schema
```

## Testing on Raspberry Pi

1. Copy backend to Pi
2. Edit `config.toml` with actual GPIO pins
3. Install `RPi.GPIO` (includes real hardware support)
4. Run `python main.py`

Without real hardware, it runs in mock mode. Sensors return simulated data.

## Real Hardware Integration

When hardware arrives:

1. Update `config.toml` with correct pins
2. Set `use_real_gpio=True` in `GPIO()`
3. Implement real sensor reading in `SensorReader`
4. No API changes needed — everything stays compatible

## Development

Run tests:

```bash
pytest
```

Format code:

```bash
black .
```

Type check:

```bash
mypy .
```

## Built-in Profiles

- **classic-9bar** — Flat 9 bar throughout
- **turbo-bloom** — Fast ramp, early spike
- **slayer-style** — Low pre-infusion, plateau, decline

Add new profiles in `models/profile.py` or via API (coming soon).

## Future Phases

- **Phase 2:** Scale integration, dosing by weight
- **Phase 3:** Visualizer.coffee export
- **Phase 4:** Theme system API
- **Phase 5:** Machine learning shot recommendations

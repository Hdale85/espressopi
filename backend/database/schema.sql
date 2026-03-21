-- EspressoPi SQLite Schema

CREATE TABLE IF NOT EXISTS shots (
    id TEXT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    duration REAL NOT NULL,
    volume REAL NOT NULL,
    pressure_peak REAL NOT NULL,
    pressure_avg REAL NOT NULL,
    temperature_avg REAL NOT NULL,
    extraction_yield REAL NOT NULL,
    profile_name TEXT NOT NULL,
    pressure_curve TEXT,  -- JSON array of pressure readings
    temperature_readings TEXT,  -- JSON array of temp readings
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS profiles (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    author TEXT DEFAULT 'user',
    points TEXT NOT NULL,  -- JSON array of profile points
    is_builtin BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS themes (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    author TEXT DEFAULT 'user',
    config TEXT NOT NULL,  -- JSON theme config
    is_active BOOLEAN DEFAULT 0,
    is_builtin BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS machine_state (
    id INTEGER PRIMARY KEY,
    boiler_temp REAL,
    steam_pressure REAL,
    water_level REAL,
    last_update DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_shots_timestamp ON shots(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_shots_profile ON shots(profile_name);
CREATE INDEX IF NOT EXISTS idx_profiles_name ON profiles(name);
CREATE INDEX IF NOT EXISTS idx_themes_name ON themes(name);

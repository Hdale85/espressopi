"""Database initialization and helpers."""
import sqlite3
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from models.shot import Shot
from models.profile import Profile, PROFILES


logger = logging.getLogger(__name__)


class Database:
    """SQLite database manager for EspressoPi."""
    
    def __init__(self, db_path: str = "./data/shots.db"):
        """Initialize database connection."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection: Optional[sqlite3.Connection] = None
    
    def connect(self):
        """Open database connection."""
        self.connection = sqlite3.connect(str(self.db_path))
        self.connection.row_factory = sqlite3.Row
        logger.info(f"Connected to database: {self.db_path}")
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def init_schema(self):
        """Initialize database schema from schema.sql."""
        schema_path = Path(__file__).parent / "schema.sql"
        
        if not schema_path.exists():
            logger.error(f"Schema file not found: {schema_path}")
            return
        
        with open(schema_path, "r") as f:
            schema = f.read()
        
        cursor = self.connection.cursor()
        cursor.executescript(schema)
        self.connection.commit()
        
        # Load built-in profiles
        self._load_builtin_profiles()
        
        logger.info("Database schema initialized")
    
    def _load_builtin_profiles(self):
        """Load default pressure profiles into database."""
        for key, profile in PROFILES.items():
            try:
                self.save_profile(profile, is_builtin=True)
            except sqlite3.IntegrityError:
                # Profile already exists
                pass
    
    # ─── SHOTS ───
    
    def save_shot(self, shot: Shot) -> bool:
        """Save a shot to database."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT INTO shots (
                    id, timestamp, duration, volume, 
                    pressure_peak, pressure_avg, temperature_avg, 
                    extraction_yield, profile_name,
                    pressure_curve, temperature_readings, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    shot.id,
                    shot.timestamp.isoformat(),
                    shot.duration,
                    shot.volume,
                    shot.stats.pressure_peak,
                    shot.stats.pressure_avg,
                    shot.stats.temp_avg,
                    shot.stats.extraction_yield,
                    shot.profile_name,
                    json.dumps(shot.pressure_curve),
                    json.dumps(shot.temperature_readings),
                    shot.notes,
                ),
            )
            self.connection.commit()
            logger.info(f"Saved shot {shot.id}")
            return True
        except Exception as e:
            logger.error(f"Error saving shot: {e}")
            return False
    
    def get_shot(self, shot_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a shot by ID."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM shots WHERE id = ?", (shot_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_shots(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get recent shots."""
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT * FROM shots ORDER BY timestamp DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def get_shots_by_profile(self, profile_name: str) -> List[Dict[str, Any]]:
        """Get all shots using a specific profile."""
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT * FROM shots WHERE profile_name = ? ORDER BY timestamp DESC",
            (profile_name,),
        )
        return [dict(row) for row in cursor.fetchall()]
    
    # ─── PROFILES ───
    
    def save_profile(self, profile: Profile, is_builtin: bool = False) -> bool:
        """Save a pressure profile."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO profiles (
                    id, name, description, author, points, is_builtin
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    f"{profile.name.lower().replace(' ', '-')}",
                    profile.name,
                    profile.description,
                    profile.author,
                    json.dumps([(p.time, p.pressure) for p in profile.points]),
                    1 if is_builtin else 0,
                ),
            )
            self.connection.commit()
            logger.info(f"Saved profile: {profile.name}")
            return True
        except Exception as e:
            logger.error(f"Error saving profile: {e}")
            return False
    
    def get_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve a profile by name."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM profiles WHERE name = ?", (name,))
        return dict(cursor.fetchone()) if cursor.fetchone() else None
    
    def get_all_profiles(self) -> List[Dict[str, Any]]:
        """Get all available profiles."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM profiles ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]
    
    # ─── MACHINE STATE ───
    
    def update_machine_state(
        self,
        boiler_temp: Optional[float] = None,
        steam_pressure: Optional[float] = None,
        water_level: Optional[float] = None,
    ):
        """Update current machine state."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO machine_state (id, boiler_temp, steam_pressure, water_level)
                VALUES (1, ?, ?, ?)
                """,
                (boiler_temp, steam_pressure, water_level),
            )
            self.connection.commit()
        except Exception as e:
            logger.error(f"Error updating machine state: {e}")
    
    def get_machine_state(self) -> Optional[Dict[str, Any]]:
        """Get current machine state."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM machine_state WHERE id = 1")
        row = cursor.fetchone()
        return dict(row) if row else None


# Global database instance
_db: Optional[Database] = None


def init_database(db_path: str = "./data/shots.db") -> Database:
    """Initialize and return database instance."""
    global _db
    _db = Database(db_path)
    _db.connect()
    _db.init_schema()
    return _db


def get_database() -> Database:
    """Get database instance."""
    global _db
    if _db is None:
        _db = Database()
        _db.connect()
    return _db

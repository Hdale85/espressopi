"""Shot data model."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class ShotStats:
    """Statistics for a completed shot."""
    duration: float          # seconds
    volume: float            # ml
    pressure_peak: float     # bar
    pressure_avg: float      # bar
    temp_avg: float          # °C
    extraction_yield: float  # %


@dataclass
class Shot:
    """A single espresso shot."""
    id: str                  # Unique identifier (UUID)
    timestamp: datetime      # When shot started
    duration: float          # seconds
    volume: float            # ml extracted
    pressure_curve: List[float]  # Pressure readings over time
    temperature_readings: List[float]  # Temp readings
    profile_name: str        # Pressure profile used
    stats: ShotStats = field(default_factory=lambda: ShotStats(0, 0, 0, 0, 0, 0))
    notes: str = ""          # User notes
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "duration": self.duration,
            "volume": self.volume,
            "pressure_curve": self.pressure_curve,
            "temperature_readings": self.temperature_readings,
            "profile_name": self.profile_name,
            "stats": {
                "duration": self.stats.duration,
                "volume": self.stats.volume,
                "pressure_peak": self.stats.pressure_peak,
                "pressure_avg": self.stats.pressure_avg,
                "temp_avg": self.stats.temp_avg,
                "extraction_yield": self.stats.extraction_yield,
            },
            "notes": self.notes,
        }

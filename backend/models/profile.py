"""Pressure profile model."""
from dataclasses import dataclass
from typing import List


@dataclass
class ProfilePoint:
    """A single point on a pressure curve."""
    time: float   # seconds
    pressure: float  # bar


@dataclass
class Profile:
    """A pressure profile (target curve for a shot)."""
    name: str
    description: str
    points: List[ProfilePoint]  # Sorted by time
    author: str = "default"
    
    def get_pressure_at_time(self, time: float) -> float:
        """Interpolate pressure at given time."""
        if not self.points:
            return 0.0
        
        # Find surrounding points
        if time <= self.points[0].time:
            return self.points[0].pressure
        if time >= self.points[-1].time:
            return self.points[-1].pressure
        
        for i in range(len(self.points) - 1):
            p1 = self.points[i]
            p2 = self.points[i + 1]
            
            if p1.time <= time <= p2.time:
                # Linear interpolation
                ratio = (time - p1.time) / (p2.time - p1.time)
                return p1.pressure + (p2.pressure - p1.pressure) * ratio
        
        return self.points[-1].pressure
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "author": self.author,
            "points": [
                {"time": p.time, "pressure": p.pressure}
                for p in self.points
            ],
        }


# Built-in profiles
CLASSIC_9BAR = Profile(
    name="Classic 9-Bar",
    description="Flat 9 bar throughout extraction",
    author="default",
    points=[
        ProfilePoint(0.0, 0.0),
        ProfilePoint(1.0, 3.0),    # Pre-infusion ramp
        ProfilePoint(2.0, 9.0),    # Rise to 9 bar
        ProfilePoint(25.0, 9.0),   # Hold at 9 bar
        ProfilePoint(30.0, 8.0),   # Gentle decline
    ],
)

TURBO_BLOOM = Profile(
    name="Turbo Bloom",
    description="Fast ramp, early pressure spike",
    author="default",
    points=[
        ProfilePoint(0.0, 0.0),
        ProfilePoint(0.5, 2.0),
        ProfilePoint(1.5, 9.5),
        ProfilePoint(20.0, 9.5),
        ProfilePoint(28.0, 7.0),
    ],
)

SLAYER_STYLE = Profile(
    name="Slayer Style",
    description="Low pre-infusion, plateau, decline",
    author="default",
    points=[
        ProfilePoint(0.0, 0.0),
        ProfilePoint(2.0, 2.0),    # Low pre-infusion
        ProfilePoint(4.0, 6.0),    # Gradual rise
        ProfilePoint(6.0, 9.0),    # Quick rise to 9
        ProfilePoint(22.0, 9.0),   # Hold
        ProfilePoint(30.0, 6.0),   # Decline
    ],
)

PROFILES = {
    "classic-9bar": CLASSIC_9BAR,
    "turbo-bloom": TURBO_BLOOM,
    "slayer-style": SLAYER_STYLE,
}

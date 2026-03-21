"""Sensor reading abstraction. Supports mock and real hardware."""
from dataclasses import dataclass
import time
import math


@dataclass
class SensorReading:
    """A single sensor reading."""
    timestamp: float
    value: float
    unit: str


class SensorReader:
    """
    Abstract sensor reader.
    Switch between mock and real implementations based on config.
    """
    
    def __init__(self, sensor_type: str, config: dict = None):
        """Initialize sensor reader."""
        self.sensor_type = sensor_type
        self.config = config or {}
        self.is_mocking = True  # Mock mode by default
        self._shot_start_time = None
    
    def read_pressure_brew(self) -> SensorReading:
        """Read brew pressure (0-15 bar)."""
        if self.is_mocking:
            return self._mock_pressure_brew()
        # TODO: Real ADS1256 + transducer reading
        raise NotImplementedError("Real hardware not yet implemented")
    
    def read_pressure_steam(self) -> SensorReading:
        """Read steam/boiler pressure (0-60 PSI)."""
        if self.is_mocking:
            return self._mock_pressure_steam()
        # TODO: Real ADS1256 reading
        raise NotImplementedError("Real hardware not yet implemented")
    
    def read_temperature(self) -> SensorReading:
        """Read group head temperature."""
        if self.is_mocking:
            return self._mock_temperature()
        # TODO: Real MAX31855 reading
        raise NotImplementedError("Real hardware not yet implemented")
    
    def read_water_level(self) -> SensorReading:
        """Read water tank level (0-100%)."""
        if self.is_mocking:
            return self._mock_water_level()
        # TODO: Real analog reading
        raise NotImplementedError("Real hardware not yet implemented")
    
    # ─── MOCK IMPLEMENTATIONS ───
    
    def _mock_pressure_brew(self) -> SensorReading:
        """Simulate pressure during shot."""
        now = time.time()
        
        if self._shot_start_time is None:
            # Idle pressure: slight variance around 1 bar
            pressure = 1.0 + math.sin(now * 0.5) * 0.2
        else:
            elapsed = now - self._shot_start_time
            
            if elapsed < 2.0:
                # Pre-infusion: ramp from 0 to 3 bar
                pressure = (elapsed / 2.0) * 3.0
            elif elapsed < 4.0:
                # Ramp to 9 bar
                progress = (elapsed - 2.0) / 2.0
                pressure = 3.0 + progress * 6.0
            elif elapsed < 25.0:
                # Plateau at 9 bar with small noise
                pressure = 9.0 + math.sin(elapsed * 2.0) * 0.2
            elif elapsed < 35.0:
                # Decline
                progress = (elapsed - 25.0) / 10.0
                pressure = 9.0 - progress * 3.0
            else:
                # Shot over
                pressure = 0.5
                self._shot_start_time = None
        
        return SensorReading(
            timestamp=now,
            value=max(0, pressure),
            unit="bar"
        )
    
    def _mock_pressure_steam(self) -> SensorReading:
        """Simulate boiler pressure (steady at 1.2 bar when ready)."""
        return SensorReading(
            timestamp=time.time(),
            value=1.2 + math.sin(time.time() * 0.2) * 0.05,
            unit="bar"
        )
    
    def _mock_temperature(self) -> SensorReading:
        """Simulate group head temperature."""
        now = time.time()
        
        if self._shot_start_time is None:
            # Idle: stable at 93°C
            temp = 93.0 + math.sin(now * 0.1) * 0.5
        else:
            elapsed = now - self._shot_start_time
            # During shot: slight rise then recovery
            temp = 93.0 + math.sin(elapsed * 0.5) * 1.5
        
        return SensorReading(
            timestamp=now,
            value=temp,
            unit="°C"
        )
    
    def _mock_water_level(self) -> SensorReading:
        """Simulate water tank level."""
        # Starts at 70%, drains slowly during shots
        level = 70.0
        
        if self._shot_start_time is not None:
            elapsed = time.time() - self._shot_start_time
            level -= elapsed * 0.5  # Drain ~0.5% per second
        
        return SensorReading(
            timestamp=time.time(),
            value=max(0, min(100, level)),
            unit="%"
        )
    
    # ─── SHOT CONTROL ───
    
    def start_shot(self):
        """Signal that a shot has started."""
        self._shot_start_time = time.time()
    
    def stop_shot(self):
        """Signal that a shot has ended."""
        self._shot_start_time = None

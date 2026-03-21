"""Shot control logic: pressure profiling, timing, volumetric control."""
import logging
import time
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Callable

from models.shot import Shot, ShotStats
from models.profile import Profile, PROFILES
from hardware.sensors import SensorReader
from hardware.gpio import GPIO


logger = logging.getLogger(__name__)


class ShotState(Enum):
    """Shot states."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


class ShotController:
    """
    Manages a single shot execution.
    Handles pressure profiling, timing, volumetric dosing, safety cutoffs.
    """
    
    def __init__(
        self,
        sensors: SensorReader,
        gpio: GPIO,
        profile: Profile,
        config: dict = None,
    ):
        """Initialize shot controller."""
        self.sensors = sensors
        self.gpio = gpio
        self.profile = profile
        self.config = config or {}
        
        # Shot state
        self.state = ShotState.IDLE
        self.shot: Optional[Shot] = None
        self.start_time: Optional[float] = None
        
        # Live data collection
        self.pressure_readings = []
        self.temp_readings = []
        self.volume_ml = 0.0
        
        # Configuration thresholds
        self.max_shot_time = self.config.get("shot_control", {}).get("max_shot_time", 45)
        self.volumetric_target = self.config.get("shot_control", {}).get("volumetric_dose_target", 38)
        
        # Callbacks
        self.on_shot_started: Optional[Callable] = None
        self.on_shot_stopped: Optional[Callable] = None
        self.on_pressure_update: Optional[Callable[[float], None]] = None
    
    def start_shot(self) -> Shot:
        """
        Start a new shot with the configured profile.
        Returns the Shot object for tracking.
        """
        if self.state != ShotState.IDLE:
            raise RuntimeError(f"Cannot start shot: state is {self.state.value}")
        
        logger.info(f"Starting shot with profile: {self.profile.name}")
        
        # Initialize shot
        self.shot = Shot(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            duration=0,
            volume=0,
            pressure_curve=[],
            temperature_readings=[],
            profile_name=self.profile.name,
        )
        
        self.start_time = time.time()
        self.pressure_readings = []
        self.temp_readings = []
        self.volume_ml = 0.0
        self.state = ShotState.RUNNING
        
        # Signal hardware
        self.sensors.start_shot()
        self.gpio.pump_enable(True)
        self.gpio.group_solenoid(True)
        self.gpio.status_led(True)
        
        if self.on_shot_started:
            self.on_shot_started()
        
        return self.shot
    
    def stop_shot(self) -> Shot:
        """Stop the current shot and return final Shot object."""
        if self.state != ShotState.RUNNING:
            logger.warning(f"Shot stop requested but state is {self.state.value}")
        
        logger.info("Shot stopped")
        
        # Stop hardware
        self.gpio.pump_enable(False)
        self.gpio.group_solenoid(False)
        self.gpio.status_led(False)
        self.sensors.stop_shot()
        
        # Finalize shot
        self.state = ShotState.STOPPED
        elapsed = time.time() - self.start_time
        
        if self.shot:
            self.shot.duration = elapsed
            self.shot.pressure_curve = self.pressure_readings
            self.shot.temperature_readings = self.temp_readings
            self.shot.volume = self.volume_ml
            
            # Calculate stats
            self.shot.stats = self._calculate_stats()
        
        if self.on_shot_stopped:
            self.on_shot_stopped()
        
        return self.shot
    
    def update(self):
        """
        Call this frequently (10-50 Hz) to:
        1. Read sensors
        2. Check pressure vs. profile
        3. Adjust pump/solenoid
        4. Check safety cutoffs
        5. Collect data for graphing
        """
        if self.state != ShotState.RUNNING:
            return
        
        elapsed = time.time() - self.start_time
        
        # Safety: max shot time
        if elapsed > self.max_shot_time:
            logger.warning(f"Max shot time exceeded ({self.max_shot_time}s)")
            self.stop_shot()
            return
        
        # Read sensors
        pressure_reading = self.sensors.read_pressure_brew()
        temp_reading = self.sensors.read_temperature()
        
        # Store readings
        self.pressure_readings.append(pressure_reading.value)
        self.temp_readings.append(temp_reading.value)
        
        # Get target pressure from profile
        target_pressure = self.profile.get_pressure_at_time(elapsed)
        
        # Simple PID-like pressure control (stub)
        # In real version: adjust pump speed or solenoid to match target
        self._adjust_pressure(pressure_reading.value, target_pressure)
        
        # Volumetric dosing: stop when we hit target ml
        if self.volumetric_target > 0:
            self.volume_ml = self._estimate_volume(elapsed)
            if self.volume_ml >= self.volumetric_target:
                logger.info(f"Volumetric target reached: {self.volume_ml:.1f}ml")
                self.stop_shot()
                return
        
        # Notify listeners
        if self.on_pressure_update:
            self.on_pressure_update(pressure_reading.value)
    
    def _adjust_pressure(self, current: float, target: float):
        """
        Adjust pump speed/solenoid to match target pressure.
        Stub: real version would use DAC + PID control.
        """
        error = target - current
        # Adjustments would happen here
        pass
    
    def _estimate_volume(self, elapsed: float) -> float:
        """Estimate volume based on time and pump characteristics."""
        # Stub: real version would use pulse counting from KNF pump
        # For now: linear estimate at ~1.5ml/sec
        if elapsed < 2:  # Pre-infusion
            return 0
        return (elapsed - 2) * 1.5
    
    def _calculate_stats(self) -> ShotStats:
        """Calculate shot statistics."""
        if not self.pressure_readings:
            return ShotStats(0, 0, 0, 0, 0, 0)
        
        duration = self.shot.duration if self.shot else 0
        pressure_peak = max(self.pressure_readings) if self.pressure_readings else 0
        pressure_avg = sum(self.pressure_readings) / len(self.pressure_readings)
        temp_avg = sum(self.temp_readings) / len(self.temp_readings) if self.temp_readings else 0
        
        # Extraction yield: (output weight / input dose) * 100
        # Stub: needs scale integration
        yield_pct = (self.volume_ml / 18.0) * 100 if self.volume_ml > 0 else 0
        
        return ShotStats(
            duration=duration,
            volume=self.volume_ml,
            pressure_peak=pressure_peak,
            pressure_avg=pressure_avg,
            temp_avg=temp_avg,
            extraction_yield=yield_pct,
        )
    
    def get_current_state(self) -> dict:
        """Get current shot state for WebSocket/API updates."""
        if not self.shot:
            return {"state": self.state.value}
        
        elapsed = time.time() - self.start_time if self.start_time else 0
        current_pressure = self.pressure_readings[-1] if self.pressure_readings else 0
        target_pressure = self.profile.get_pressure_at_time(elapsed)
        
        return {
            "state": self.state.value,
            "elapsed": elapsed,
            "pressure_current": current_pressure,
            "pressure_target": target_pressure,
            "volume": self.volume_ml,
            "temperature": self.temp_readings[-1] if self.temp_readings else 0,
            "shot_id": self.shot.id,
        }

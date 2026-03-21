"""GPIO control abstraction for pump, solenoids, etc."""
import logging


logger = logging.getLogger(__name__)


class GPIO:
    """
    GPIO handler for pump and solenoid control.
    Mocked by default; real RPi.GPIO implementation can be swapped in.
    """
    
    def __init__(self, config: dict = None, use_real_gpio: bool = False):
        """Initialize GPIO handler."""
        self.config = config or {}
        self.use_real_gpio = use_real_gpio
        self._state = {}
        
        # Pin assignments from config
        self.pump_pin = self.config.get("pump_enable_pin", 23)
        self.group_solenoid_pin = self.config.get("group_solenoid_pin", 24)
        self.steam_solenoid_pin = self.config.get("steam_solenoid_pin", 25)
        self.status_led_pin = self.config.get("status_led_pin", 27)
        
        # Initialize pin states
        self._state[self.pump_pin] = False
        self._state[self.group_solenoid_pin] = False
        self._state[self.steam_solenoid_pin] = False
        self._state[self.status_led_pin] = False
        
        if self.use_real_gpio:
            self._init_real_gpio()
        else:
            logger.info("GPIO: Using mock mode (no real hardware)")
    
    def _init_real_gpio(self):
        """Initialize real RPi.GPIO (placeholder)."""
        try:
            import RPi.GPIO as GPIO_LIB
            GPIO_LIB.setmode(GPIO_LIB.BCM)
            
            # Set all pins as outputs
            for pin in [self.pump_pin, self.group_solenoid_pin, self.steam_solenoid_pin, self.status_led_pin]:
                GPIO_LIB.setup(pin, GPIO_LIB.OUT)
                GPIO_LIB.output(pin, GPIO_LIB.LOW)
            
            logger.info("GPIO: Real hardware initialized")
        except ImportError:
            logger.warning("RPi.GPIO not available; falling back to mock mode")
            self.use_real_gpio = False
    
    def pump_enable(self, state: bool):
        """Enable/disable pump."""
        self._set_pin(self.pump_pin, state, "pump")
    
    def group_solenoid(self, state: bool):
        """Open/close group solenoid."""
        self._set_pin(self.group_solenoid_pin, state, "group_solenoid")
    
    def steam_solenoid(self, state: bool):
        """Open/close steam solenoid."""
        self._set_pin(self.steam_solenoid_pin, state, "steam_solenoid")
    
    def status_led(self, state: bool):
        """Control status LED."""
        self._set_pin(self.status_led_pin, state, "status_led")
    
    def _set_pin(self, pin: int, state: bool, name: str):
        """Set a GPIO pin (real or mock)."""
        self._state[pin] = state
        
        if self.use_real_gpio:
            try:
                import RPi.GPIO as GPIO_LIB
                GPIO_LIB.output(pin, GPIO_LIB.HIGH if state else GPIO_LIB.LOW)
            except Exception as e:
                logger.error(f"GPIO error on {name}: {e}")
        
        logger.debug(f"GPIO {name} ({pin}): {'ON' if state else 'OFF'}")
    
    def get_state(self, pin: int) -> bool:
        """Get current state of a pin."""
        return self._state.get(pin, False)
    
    def all_off(self):
        """Turn off all control pins (emergency stop)."""
        self.pump_enable(False)
        self.group_solenoid(False)
        self.steam_solenoid(False)
        logger.warning("GPIO: All outputs turned OFF")
    
    def cleanup(self):
        """Clean up GPIO resources."""
        self.all_off()
        
        if self.use_real_gpio:
            try:
                import RPi.GPIO as GPIO_LIB
                GPIO_LIB.cleanup()
                logger.info("GPIO: Cleanup complete")
            except Exception as e:
                logger.error(f"GPIO cleanup error: {e}")

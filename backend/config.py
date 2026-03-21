"""
Configuration loader for EspressoPi.
Reads config.toml and provides typed config objects.
"""
import os
from typing import Dict, Any
import tomli
from pathlib import Path


class Config:
    """Main configuration object."""
    
    def __init__(self, config_path: str = "config.toml"):
        """Load config from TOML file."""
        self.path = Path(config_path)
        
        if not self.path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(self.path, "rb") as f:
            self.data = tomli.load(f)
        
        # Extract sections
        self.machine = self.data.get("machine", {})
        self.sensors = self.data.get("sensors", {})
        self.gpio = self.data.get("gpio", {})
        self.hardware = self.data.get("hardware", {})
        self.profiles = self.data.get("profiles", {})
        self.shot_control = self.data.get("shot_control", {})
        self.database = self.data.get("database", {})
        self.api = self.data.get("api", {})
        self.logging = self.data.get("logging", {})
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get a config value by section and key."""
        section_data = getattr(self, section.lower(), {})
        return section_data.get(key, default)
    
    def validate(self) -> bool:
        """Validate critical config values."""
        required = [
            ("machine", "name"),
            ("database", "path"),
            ("api", "port"),
        ]
        
        for section, key in required:
            if not self.get(section, key):
                raise ValueError(f"Missing required config: {section}.{key}")
        
        return True
    
    def __repr__(self) -> str:
        return f"<Config: {self.machine.get('name', 'unnamed')}>"


# Global config instance
_config: Config | None = None


def load_config(path: str = "config.toml") -> Config:
    """Load configuration from file."""
    global _config
    _config = Config(path)
    _config.validate()
    return _config


def get_config() -> Config:
    """Get loaded config instance."""
    global _config
    if _config is None:
        _config = load_config()
    return _config

"""
Simple configuration loader for I AM SPLITTER
"""
import yaml
from pathlib import Path
from typing import Dict, Any, List

class Config:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            print(f"⚠️  Config file {self.config_path} not found, using defaults")
            return self._get_defaults()
        
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                print(f"✅ Loaded config from {self.config_path}")
                return config
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return self._get_defaults()
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Default configuration values"""
        return {
            "model": {
                "name": "htdemucs"
            },
            "audio": {
                "supported_formats": [".wav", ".mp3", ".flac", ".m4a", ".aiff", ".ogg"],
                "max_file_size": 100
            },
            "api": {
                "title": "I AM SPLITTER API",
                "description": "AI-powered audio stem separation service",
                "version": "1.0.0",
                "cors_origins": ["http://localhost:3000"]
            }
        }
    
    def get(self, key: str, default=None):
        """Get config value using dot notation (e.g., 'model.name')"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

# Global config instance
config = Config()
print(config.get("audio.supported_formats"))
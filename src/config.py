"""
Configuration management for Starlink monitoring system.
Ensures Linux OS compatibility for directory paths.
"""
import os
from pathlib import Path

# Linux-compatible directory paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Try to use system directories, fall back to local if no permissions
def _get_log_dir():
    system_log = Path("/var/log/starlink-monitor")
    if os.path.exists("/var/log"):
        try:
            system_log.mkdir(parents=True, exist_ok=True)
            return system_log
        except PermissionError:
            pass
    local_log = BASE_DIR / "logs"
    local_log.mkdir(parents=True, exist_ok=True)
    return local_log

def _get_data_dir():
    system_data = Path("/var/lib/starlink-monitor")
    if os.path.exists("/var/lib"):
        try:
            system_data.mkdir(parents=True, exist_ok=True)
            return system_data
        except PermissionError:
            pass
    local_data = BASE_DIR / "data"
    local_data.mkdir(parents=True, exist_ok=True)
    return local_data

LOG_DIR = _get_log_dir()
DATA_DIR = _get_data_dir()

# Starlink API configuration
STARLINK_STATUS_ENDPOINT = os.getenv("STARLINK_API_ENDPOINT", "http://192.168.100.1/api/status")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "10"))

# Monitoring configuration
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "5"))  # seconds
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# Metrics thresholds for event detection
LATENCY_THRESHOLD = float(os.getenv("LATENCY_THRESHOLD", "100"))  # ms
DOWNLINK_THRESHOLD = float(os.getenv("DOWNLINK_THRESHOLD", "50"))  # Mbps
UPLINK_THRESHOLD = float(os.getenv("UPLINK_THRESHOLD", "10"))  # Mbps
OBSTRUCTION_THRESHOLD = float(os.getenv("OBSTRUCTION_THRESHOLD", "5"))  # percentage

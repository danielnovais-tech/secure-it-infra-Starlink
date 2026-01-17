"""
Starlink API client for retrieving real-time status and metrics.
Replaces simulations with actual API calls to Starlink's status endpoint.
"""
import requests
import logging
from typing import Dict, Optional, Any
from datetime import datetime, timezone
from src.config import STARLINK_STATUS_ENDPOINT, API_TIMEOUT, MAX_RETRIES

logger = logging.getLogger(__name__)


class StarlinkAPIClient:
    """Client for interacting with Starlink's status API endpoint."""
    
    def __init__(self, endpoint: str = STARLINK_STATUS_ENDPOINT):
        """
        Initialize the Starlink API client.
        
        Args:
            endpoint: The Starlink API endpoint URL
        """
        self.endpoint = endpoint
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SecureIT-Starlink-Monitor/1.0'
        })
    
    def get_status(self) -> Optional[Dict[str, Any]]:
        """
        Fetch current status from Starlink API.
        
        Returns:
            Dictionary containing status data or None if request fails
        """
        retries = 0
        while retries < MAX_RETRIES:
            try:
                response = self.session.get(
                    self.endpoint,
                    timeout=API_TIMEOUT
                )
                response.raise_for_status()
                data = response.json()
                logger.debug(f"Successfully retrieved status from {self.endpoint}")
                return self._parse_status(data)
            except requests.exceptions.Timeout:
                retries += 1
                logger.warning(f"Timeout connecting to {self.endpoint}, retry {retries}/{MAX_RETRIES}")
            except requests.exceptions.ConnectionError as e:
                retries += 1
                logger.warning(f"Connection error to {self.endpoint}: {e}, retry {retries}/{MAX_RETRIES}")
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error from {self.endpoint}: {e}")
                return None
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error: {e}")
                return None
            except ValueError as e:
                logger.error(f"Invalid JSON response: {e}")
                return None
        
        logger.error(f"Failed to get status after {MAX_RETRIES} retries")
        return None
    
    def _parse_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and normalize status data from API response.
        
        Args:
            data: Raw API response data
            
        Returns:
            Normalized metrics dictionary
        """
        # Extract relevant metrics from Starlink API response
        # The actual structure depends on the Starlink API format
        metrics = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'uptime': data.get('uptime', 0),
            'state': data.get('state', 'UNKNOWN'),
            'alerts': data.get('alerts', {}),
        }
        
        # Network performance metrics
        if 'popPingLatencyMs' in data:
            metrics['latency_ms'] = data.get('popPingLatencyMs', 0)
        
        if 'downlinkThroughputBps' in data:
            metrics['downlink_mbps'] = data.get('downlinkThroughputBps', 0) / 1_000_000
        
        if 'uplinkThroughputBps' in data:
            metrics['uplink_mbps'] = data.get('uplinkThroughputBps', 0) / 1_000_000
        
        # Obstruction metrics
        if 'obstructionStats' in data:
            obstruction = data.get('obstructionStats', {})
            metrics['obstruction_percent'] = obstruction.get('fractionObstructed', 0) * 100
            metrics['avg_obstruction_duration'] = obstruction.get('avgProlongedObstructionDurationS', 0)
        
        # SNR (Signal-to-Noise Ratio)
        if 'snr' in data:
            metrics['snr'] = data.get('snr', 0)
        
        # Downtime metrics
        if 'downtimeSeconds' in data:
            metrics['downtime_seconds'] = data.get('downtimeSeconds', 0)
        
        # Hardware temperature
        if 'dishGetStatus' in data:
            dish_status = data.get('dishGetStatus', {})
            metrics['temperature_c'] = dish_status.get('deviceTemperature', {}).get('avg', 0)
        
        return metrics
    
    def close(self):
        """Close the session."""
        self.session.close()

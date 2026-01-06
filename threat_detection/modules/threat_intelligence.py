"""
Threat Intelligence Feed Updater
Downloads and processes threat intelligence feeds from DShield and Emerging Threats
"""

import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Set
import urllib.request
import urllib.error


class ThreatIntelligenceUpdater:
    """Updates threat intelligence feeds from external sources"""
    
    def __init__(self, config: dict):
        """
        Initialize threat intelligence updater with configuration
        
        Args:
            config: Dictionary containing threat intelligence settings
        """
        self.config = config
        self.feeds = config.get('feeds', {})
        self.update_interval_hours = config.get('update_interval_hours', 6)
        self.last_update = {}
        self.threat_ips = set()
        
    def _download_feed(self, url: str) -> str:
        """
        Download content from a URL
        
        Args:
            url: URL to download from
            
        Returns:
            Content of the URL as string
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Threat Detection System)'
            }
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.read().decode('utf-8', errors='ignore')
        except urllib.error.URLError as e:
            print(f"Error downloading feed from {url}: {e}")
            return ""
        except Exception as e:
            print(f"Unexpected error downloading feed from {url}: {e}")
            return ""
    
    def _parse_dshield_feed(self, content: str) -> Set[str]:
        """
        Parse DShield format feed
        
        Args:
            content: Raw feed content
            
        Returns:
            Set of IP addresses
        """
        ips = set()
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # DShield format: IP_ADDRESS	NETMASK	ATTACKS
            parts = line.split('\t')
            if len(parts) >= 1:
                ip = parts[0].strip()
                # Basic IP validation
                if self._is_valid_ip(ip):
                    ips.add(ip)
        
        return ips
    
    def _parse_plain_ip_list(self, content: str) -> Set[str]:
        """
        Parse plain IP list format feed
        
        Args:
            content: Raw feed content
            
        Returns:
            Set of IP addresses
        """
        ips = set()
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Extract IP if it's the first thing on the line
            ip = line.split()[0] if line.split() else line
            
            # Basic IP validation
            if self._is_valid_ip(ip):
                ips.add(ip)
        
        return ips
    
    def _is_valid_ip(self, ip: str) -> bool:
        """
        Basic IP address validation
        
        Args:
            ip: IP address string
            
        Returns:
            True if valid IP format, False otherwise
        """
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        
        try:
            for part in parts:
                num = int(part)
                if num < 0 or num > 255:
                    return False
            return True
        except ValueError:
            return False
    
    def update_feed(self, feed_name: str, feed_config: dict) -> Set[str]:
        """
        Update a single threat intelligence feed
        
        Args:
            feed_name: Name of the feed
            feed_config: Configuration for the feed
            
        Returns:
            Set of threat IP addresses from this feed
        """
        if not feed_config.get('enabled', True):
            return set()
        
        # Check if update is needed
        now = datetime.now()
        last_update = self.last_update.get(feed_name)
        
        if last_update:
            time_since_update = (now - last_update).total_seconds() / 3600
            if time_since_update < self.update_interval_hours:
                print(f"Feed {feed_name} updated {time_since_update:.1f} hours ago, skipping")
                return set()
        
        print(f"Updating threat intelligence feed: {feed_name}")
        
        url = feed_config.get('url', '')
        feed_format = feed_config.get('format', 'plain_ip_list')
        
        # Download feed
        content = self._download_feed(url)
        if not content:
            print(f"Failed to download feed {feed_name}")
            return set()
        
        # Parse feed based on format
        if feed_format == 'dshield':
            ips = self._parse_dshield_feed(content)
        elif feed_format == 'plain_ip_list':
            ips = self._parse_plain_ip_list(content)
        else:
            print(f"Unknown feed format: {feed_format}")
            return set()
        
        self.last_update[feed_name] = now
        print(f"Feed {feed_name} updated with {len(ips)} threat IPs")
        
        return ips
    
    def update_all_feeds(self) -> Set[str]:
        """
        Update all configured threat intelligence feeds
        
        Returns:
            Combined set of all threat IP addresses
        """
        all_threat_ips = set()
        
        for feed_name, feed_config in self.feeds.items():
            ips = self.update_feed(feed_name, feed_config)
            all_threat_ips.update(ips)
        
        self.threat_ips = all_threat_ips
        print(f"Total unique threat IPs: {len(all_threat_ips)}")
        
        return all_threat_ips
    
    def is_threat_ip(self, ip_address: str) -> bool:
        """
        Check if an IP address is in the threat intelligence feeds
        
        Args:
            ip_address: IP address to check
            
        Returns:
            True if IP is a known threat, False otherwise
        """
        return ip_address in self.threat_ips
    
    def get_threat_ips(self) -> List[str]:
        """
        Get list of all known threat IPs
        
        Returns:
            List of threat IP addresses
        """
        return list(self.threat_ips)
    
    def save_threat_ips(self, file_path: str):
        """
        Save threat IPs to a file
        
        Args:
            file_path: Path to save the threat IPs
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(f"# Threat Intelligence Feed - Updated {datetime.now().isoformat()}\n")
                f.write(f"# Total IPs: {len(self.threat_ips)}\n")
                for ip in sorted(self.threat_ips):
                    f.write(f"{ip}\n")
            print(f"Threat IPs saved to {file_path}")
        except Exception as e:
            print(f"Error saving threat IPs to {file_path}: {e}")
    
    def load_threat_ips(self, file_path: str):
        """
        Load threat IPs from a file
        
        Args:
            file_path: Path to load the threat IPs from
        """
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if self._is_valid_ip(line):
                            self.threat_ips.add(line)
            print(f"Loaded {len(self.threat_ips)} threat IPs from {file_path}")
        except FileNotFoundError:
            print(f"Threat IP file not found: {file_path}")
        except Exception as e:
            print(f"Error loading threat IPs from {file_path}: {e}")

"""Security monitoring module for Starlink infrastructure."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

import aiohttp
import psutil
import yaml
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class SecurityMonitor:
    """Collect metrics, encrypt reports, and send them asynchronously.

    This is a minimal implementation added to justify the module imports and
    serve as a foundation for future Starlink infrastructure security monitoring.
    """

    def __init__(self, config_path: str | Path):
        self.config_path = Path(config_path)
        self.config: dict[str, Any] = self._load_config(self.config_path)

        key = self.config.get("fernet_key")
        if not key:
            key = Fernet.generate_key()
        if isinstance(key, str):
            key = key.encode()

        self.cipher = Fernet(key)

    @staticmethod
    def _load_config(config_path: Path) -> dict[str, Any]:
        with config_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data or {}

    def collect_metrics(self) -> dict[str, Any]:
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "connections": len(psutil.net_connections()),
        }

    def encrypt_report(self, report: dict[str, Any]) -> bytes:
        payload = yaml.safe_dump(report).encode("utf-8")
        return self.cipher.encrypt(payload)

    async def send_report(self, report: dict[str, Any]) -> None:
        url = self.config.get("report_url")
        if not url:
            raise ValueError("Missing 'report_url' in config")

        encrypted = self.encrypt_report(report)
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=encrypted) as resp:
                resp.raise_for_status()


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    config_path = Path(__file__).with_name("security_monitor.yml")
    monitor = SecurityMonitor(config_path)
    metrics = monitor.collect_metrics()
    await monitor.send_report(metrics)


if __name__ == "__main__":
    asyncio.run(main())

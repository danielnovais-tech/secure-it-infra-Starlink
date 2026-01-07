"""Security monitoring module for Starlink infrastructure."""

# Standard library imports
import asyncio
import hashlib
import json
import logging
import queue
import signal
import socket
import ssl
import subprocess
import sys
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Third-party imports
import aiohttp
import psutil
import yaml
from cryptography.fernet import Fernet

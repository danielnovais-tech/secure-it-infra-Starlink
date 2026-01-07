"""Base class for security modules"""

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..foundation import StarlinkSecurityFoundation

logger = logging.getLogger(__name__)


class SecurityModule(ABC):
    """Base class for all security modules."""
    
    def __init__(self, foundation: 'StarlinkSecurityFoundation'):
        self.foundation = foundation
        self.config = foundation.config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.running = False
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the module. Returns True if successful."""
        pass
    
    @abstractmethod
    async def start(self):
        """Start the module's async operations."""
        pass
    
    @abstractmethod
    async def stop(self):
        """Stop the module's async operations."""
        pass
    
    def cleanup(self):
        """Cleanup resources."""
        self.running = False

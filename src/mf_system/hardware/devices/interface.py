from abc import ABC, abstractmethod
from typing import Any, Dict


class IHardwareAdapter(ABC):
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the device"""
        pass

    @abstractmethod
    def execute(self, command: Dict[str, Any]) -> Any:
        """Implement the command"""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the connection"""
        pass

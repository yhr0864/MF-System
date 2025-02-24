import telnetlib
import sys
import time

from mf_system.hardware.devices.interface import IHardwareAdapter


class GantryAdapter(IHardwareAdapter):
    def __init__(self, config: dict):
        self.ip = config["ip"]
        self.port = config["port"]
        self._connection = None

    def initialize(self) -> bool:
        try:
            self._connection = telnetlib.Telnet(self.ip, self.port)
            return True
        except ConnectionError:
            return False

    def execute(self, command: dict) -> str:
        if command["action"] == "move":
            return self._connection.move_to(command["x"], command["y"])
        else:
            raise ValueError("Unsupported command")

    def shutdown(self) -> None:
        if self._connection:
            self._connection.close()

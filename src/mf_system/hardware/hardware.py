import time
import yaml
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Tuple

from mf_system.hardware.devices.interface import IHardwareAdapter
from mf_system.hardware.devices.arduino import ArduinoAdapter
from mf_system.hardware.devices.gantry import GantryAdapter
from mf_system.hardware.devices.pump import SyringePumpAdapter
from mf_system.hardware.devices.dls import DLSAdapter
from mf_system.hardware.devices.utils import (
    RequestFailed,
    UnexpectedResponse,
    ErrorOccurred,
    DeviceNotFoundError,
)


class HardwareFactory:
    @staticmethod
    def _load_config(self, file_path: str, loader) -> Dict[str, Any]:
        """Load configuration from a file using the specified loader."""
        try:
            with open(file_path, "r") as file:
                return loader(file)
        except Exception as e:
            raise FileNotFoundError(f"Failed to load config file {file_path}: {e}")

    def create_adapter(device_type: str, config: dict) -> IHardwareAdapter:
        if device_type == "Pumps":
            pumps = {}
            for p, p_config in config.items():
                pumps[p] = SyringePumpAdapter(p_config)
            return pumps
        elif device_type == "Arduino":
            return ArduinoAdapter(config)
        elif device_type == "DLS":
            return DLSAdapter(config)
        elif device_type == "Gantry":
            return GantryAdapter(config)
        else:
            raise DeviceNotFoundError(device_type)


class HardwareManager:
    def __init__(self, hardware_config_path):
        # {"Pumps": {"pump1": SyringePumpAdapter(p_config), ...}, "Arduino": ArduinoAdapter(config)}
        self.adapters: Dict[str, IHardwareAdapter] = {}
        self.hw_config = HardwareFactory._load_config(
            hardware_config_path, loader=yaml.safe_load
        )
        self._init_adapters()

    def _init_adapters(self):
        for device_type, config in self.hw_config.items():
            try:
                adapter = HardwareFactory.create_adapter(device_type, config)
                self.adapters[device_type] = adapter
            except DeviceNotFoundError as e:
                print(f"Skipped unsupported device: {e}")

    def initialize_all(self) -> Dict[str, bool]:
        results = {}
        for name, adapter in self.adapters.items():
            try:
                # initialize pumps
                if isinstance(adapter, dict):
                    results[name] = {}
                    for p_name, pump_adapter in adapter.items():
                        results[name][p_name] = pump_adapter.initialize()
                else:
                    results[name] = adapter.initialize()
            except Exception as e:
                results[name] = False
                print(f"Failed to initialize {name}: {e}")
        return results

    def execute_command(self, device: str, command: dict, pump_name=None):
        if device not in self.adapters:
            raise DeviceNotFoundError(device)
        else:
            if pump_name:  # pumps action
                return self.adapters[device][pump_name].execute(command)
            return self.adapters[device].execute(command)

    def shutdown_all(self) -> None:
        for adapter in self.adapters.values():
            if isinstance(adapter, dict):
                for pump_adapter in adapter.values():
                    pump_adapter.shutdown()
            else:
                adapter.shutdown()


if __name__ == "__main__":
    hwm = HardwareManager(
        hardware_config_path="src/mf_system/database/hardware_config.yaml",
    )

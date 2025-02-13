import time
import yaml
import json
import functools
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Tuple

from mf_system.hardware.devices.arduino import ArduinoBoard
from mf_system.hardware.devices.gantry import Gantry
from mf_system.hardware.devices.pump import SyringePump
from mf_system.hardware.devices.dls import DLS_Analyzer
from mf_system.hardware.devices.utils import (
    RequestFailed,
    UnexpectedResponse,
    ErrorOccurred,
)


class Hardware:
    def __init__(
        self,
        hardware_config_path="src/mf_system/database/hardware_config.yaml",
        sample_config_path="src/mf_system/database/sample_config.json",
    ):
        # Read the config files for the experiment
        self.hardware_config = self._load_config(
            hardware_config_path, loader=yaml.safe_load
        )
        self.sample_data = self._load_config(sample_config_path, loader=json.load)

        self.gantry = Gantry(
            excl_ip=self.hardware_config["Gantry"]["ip"],
            excl_port=self.hardware_config["Gantry"]["port"],
        )

        self.arduino = ArduinoBoard(
            port=self.hardware_config["Arduino"]["port"],
            baudrate=self.hardware_config["Arduino"]["baudrate"],
            timeout=self.hardware_config["Arduino"]["timeout"],
        )

        self.dls = DLS_Analyzer(
            port=self.hardware_config["DLS"]["port"],
            baudrate=self.hardware_config["DLS"]["baudrate"],
            timeout=self.hardware_config["DLS"]["timeout"],
        )

        # Initialize pumps dynamically (self.pumps -> dict)
        self.pumps = self._initialize_pumps()

        # Test Only
        # self.pump6 = "Pump 6 is ready"
        # self.pump2 = "Pump 2 is ready"

        self.sample_id = 0

    def _load_config(self, file_path: str, loader) -> Dict[str, Any]:
        """Load configuration from a file using the specified loader."""
        try:
            with open(file_path, "r") as file:
                return loader(file)
        except Exception as e:
            raise FileNotFoundError(f"Failed to load config file {file_path}: {e}")

    def _initialize_pumps(self) -> Dict[str, SyringePump]:
        """Initialize all pumps dynamically based on the hardware configuration."""
        pumps = {}
        for pump_id, pump_config in self.hardware_config["Pumps"].items():
            pumps[pump_id] = SyringePump(
                pump_name=pump_config["name"],
                pressure_limit=pump_config["pressure_limit"],
                inner_diameter_mm=pump_config["inner_diameter_mm"],
                max_piston_stroke_mm=pump_config["max_piston_stroke_mm"],
            )
        return pumps

    def initialize(self):
        self.gantry.initialize()
        self.arduino.initialize()
        time.sleep(1)
        print(self.home_table_p())
        print(self.home_table_m())
        print(self.home_probe_dls())
        print(self.home_probe_uv())

        self.dls.initialize()

        # Initialize all pumps
        for _, pump in self.pumps.items():
            pump.initialize()

        self.prepare_pump()

    def tray_to_pump(self, coord: Tuple[Tuple[float, float], Tuple[float, float]]):
        """Move from tray to pump."""
        coord_on_tray, coord_on_table_p = coord
        # self.gantry.move_from_to(coord_on_tray, coord_on_table_p)
        print("tray to pump")

    def tray_to_measure(self, coord: Tuple[Tuple[float, float], Tuple[float, float]]):
        """Move from tray to measurement table."""
        coord_on_tray, coord_on_table_m = coord
        # self.gantry.move_from_to(coord_on_tray, coord_on_table_m)
        print("tray to measure")

    def pump_to_measure(self, coord: Tuple[Tuple[float, float], Tuple[float, float]]):
        """Move from pump to measurement table."""
        coord_on_table_p, coord_on_table_m = coord
        # self.gantry.move_from_to(coord_on_table_p, coord_on_table_m)
        print("pump to measure")

    def pump_to_tray(self, coord: Tuple[Tuple[float, float], Tuple[float, float]]):
        """Move from pump to tray."""
        coord_on_table_p, coord_on_tray = coord
        # self.gantry.move_from_to(coord_on_table_p, coord_on_tray)
        print("pump to tray")

    def measure_to_tray(self, coord: Tuple[Tuple[float, float], Tuple[float, float]]):
        """Move from measurement table to tray."""
        coord_on_table_m, coord_on_tray = coord
        # self.gantry.move_from_to(coord_on_table_m, coord_on_tray)
        print("measure to tray")

    def home_table_p(self) -> str:
        """Home the pump table."""
        return self.arduino.send_command("motor1 home")

    def home_table_m(self) -> str:
        """Home the measurement table."""
        return self.arduino.send_command("motor2 home")

    def rotate_table_p(self) -> str:
        """Rotate the pump table."""
        return self.arduino.send_command("motor1 rotate")

    def rotate_table_m(self) -> str:
        """Rotate the measurement table."""
        return self.arduino.send_command("motor2 rotate")

    def home_probe_uv(self) -> str:
        """Home the UV probe."""
        return self.arduino.send_command("cylinder1 home")

    def home_probe_dls(self) -> str:
        """Home the DLS probe."""
        return self.arduino.send_command("cylinder2 home")

    def dip_out_probe_uv(self) -> str:
        """Extend the UV probe."""
        return self.arduino.send_command("cylinder1 extend")

    def dip_in_probe_uv(self) -> str:
        """Retract the UV probe."""
        return self.arduino.send_command("cylinder1 retract")

    def dip_out_probe_dls(self) -> str:
        """Extend the DLS probe."""
        return self.arduino.send_command("cylinder2 extend")

    def dip_in_probe_dls(self) -> str:
        """Retract the DLS probe."""
        return self.arduino.send_command("cylinder2 retract")

    def prepare_pump(self):
        """Prepare the pumps before experiemnt (e.g., charging)."""

        # Refill all the pumps in the config files (Maybe NOT ALL)
        pump_config = self.hardware_config["Pumps"]

        # Calculate the required volume for each pump
        samples = self.sample_data["samples"]
        pump_volume = {}
        for sample in samples.values():
            total_proportion = sum(sample["proportion"])
            for prop, pump_id in zip(sample["proportion"], sample["pumps"]):
                ratio = prop / total_proportion
                if pump_id in pump_volume:
                    pump_volume[pump_id] += ratio * sample["volume"]
                else:
                    pump_volume[pump_id] = ratio * sample["volume"]

        with ThreadPoolExecutor() as executor:
            futures = []
            for pump_id, config in pump_config.items():
                pump = self.pumps[pump_id]
                flow = config["flow"]

                volume = pump_volume[pump_id]

                futures.append(
                    executor.submit(
                        self.charge, pump=pump, volume=float(volume), flow=float(flow)
                    )
                )

            # Wait for all tasks to complete
            for future in futures:
                future.result()

    def refill(self, pump: SyringePump, flow: float):
        """Refill the pump with the specified flow rate."""
        pump.refill(flow)

    def empty(self, pump: SyringePump, flow: float):
        """Empty the pump with the specified flow rate."""
        pump.empty(flow)

    def charge(self, pump: SyringePump, volume: float, flow: float):
        """Charge the pump by aspirating the specified volume at the given flow rate."""
        pump.aspirate(volume, flow)

    def dose(self, pump: SyringePump, volume: float, flow: float):
        """Dispense the specified volume at the given flow rate."""
        pump.dispense(volume, flow)

    def fill_bottle(self):
        """
        Fill the bottle by dispensing from multiple pumps in parallel.
        Uses multi-threading for parallel execution.
        """

        # Load sample data
        num_samples = self.sample_data["num_samples"]
        out_flow = self.sample_data["out_flow"]
        self.sample_id += 1

        if self.sample_id > num_samples:
            raise ValueError("Sample ID is out of range!")

        sample_info = self.sample_data[str(self.sample_id)]
        volume = sample_info["volume"]
        proportion = sample_info["proportion"]
        solution = sample_info["solution"]
        pumps = sample_info["pumps"]

        # Calculate total proportion for normalization
        total_proportion = sum(proportion)

        # Parallelly dispensing with multi-threading
        with ThreadPoolExecutor() as executor:
            futures = []
            for i, pump_id in enumerate(pumps):
                ratio = proportion[i] / total_proportion
                sub_flow = out_flow * ratio
                sub_volume = volume * ratio
                pump = self.pumps[pump_id]

                futures.append(
                    executor.submit(
                        self.dose,
                        pump=pump,
                        volume=float(sub_volume),
                        flow=float(sub_flow),
                    )
                )

            # Wait for all tasks to complete
            for future in futures:
                future.result()

    def measure_DLS(self, setup_id: int, num_of_measure: int, save_path: str):
        """
        Measures DLS (Dynamic Light Scattering) data using the specified setup.

        Args:
            setup_id (int): The measurement setup index.
            num_of_measure (int): The number of measurements to take.
            save_path (str): The file path to save the measurement data.

        Returns:
            str or False: Arduino feedback message if available.
        """
        # Dip in the probe tip
        fb = self.dip_in_probe_dls()
        if fb != "Cylinder2 Retraction Finished":
            raise RequestFailed(
                "Cylinder_dls dip in request failed. Measurement cannot proceed."
            )

        # Step 1: Select the DLS measurement setup
        self.dls.select_measurement_setup(setup_index=setup_id)

        # Step 2: Run the measurement and request data
        if self.dls.request_data(num_of_runs=num_of_measure, data_file=save_path):
            # Retract the rod only if the measurement was successful
            return self.dip_out_probe_dls()

        return False

    def measure_UV(self):
        # # Dip the measure rod in the sample
        # self.arduino.send_command("rod_UV extend")

        # # Measuring

        # # Measure finished
        # self.arduino.send_command("rod_UV retract")
        print("measure uv")


if __name__ == "__main__":
    try:
        with open("src/mf_system/database/sample_config.json", "r") as file:
            sample_config = json.load(file)
            # print(hardware_config["Pumps"])
            samples = sample_config["samples"]
            pump_volume = {}
            for _, sample in samples.items():
                total_proportion = sum(sample["proportion"])
                for prop, p in zip(sample["proportion"], sample["pumps"]):
                    ratio = prop / total_proportion
                    if p in pump_volume:
                        pump_volume[p] += ratio * sample["volume"]
                    else:
                        pump_volume[p] = ratio * sample["volume"]

            # print(key)
            # pump = self.pumps[key]
            # flow = pump_config[key]["flow"]
            # volume = 0
    except Exception as e:
        raise FileNotFoundError(f"Failed to load config file : {e}")

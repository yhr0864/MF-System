import time
import logging
import json
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor

from transitions import Machine

from mf_system.hardware.hardware import HardwareManager, HardwareFactory
from mf_system.hardware.devices.utils import RequestFailed


class StateMachine:
    def __init__(
        self,
        states: List[str],
        transitions: List[dict],
        name: str,
        num_bottles: int,
        hardware_config_path: str,
        sample_config_path: str,
        test_mode: bool = False,
        initial: str = "initialize",
        ignore_invalid_triggers: bool = True,
        auto_transitions: bool = False,
    ):
        self.machine = Machine(
            model=self,
            states=states,
            transitions=transitions,
            initial=initial,
            name=name,
            ignore_invalid_triggers=ignore_invalid_triggers,
            auto_transitions=auto_transitions,
        )

        self.hardware: Optional[HardwareManager] = (
            None if test_mode else HardwareManager(hardware_config_path)
        )
        self.sample_config = self._load_sample_config(sample_config_path)
        self.sample_id = 0
        self.feedback = None

        self.num_bottles = num_bottles
        self.current_num_bottles = num_bottles
        self.running = True

    @property
    def is_bottle_on_tray(self) -> bool:
        return self.current_num_bottles > 0

    def _load_sample_config(self, sample_config_path):
        HardwareFactory._load_config(sample_config_path, loader=json.load)

    def initialize(self):
        if self.hardware:
            res = self.hardware.initialize_all()

        self.trigger("initialize_finished")

    def auto_run(self):
        while self.running:
            action = getattr(self, self.state, lambda: None)
            action()
            time.sleep(1)

    def stop(self):
        """Gracefully stop the auto-run loop."""
        self.running = False

    def prepare_pump(self):
        """Prepare the pumps before experiemnt (e.g., charging)."""

        # Refill all the pumps in the config files (Maybe NOT ALL)
        pump_config = self.hardware.hw_config["Pumps"]

        # Calculate the required volume for each pump
        samples = self.sample_config["samples"]
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
                flow = config["flow"]
                volume = pump_volume[pump_id]

                futures.append(
                    executor.submit(
                        self.hardware.execute_command,
                        "Pumps",
                        {"action": "aspirate", "volume": volume, "flow": flow},
                        pump_id,
                    )
                )

            # Wait for all tasks to complete
            for future in futures:
                future.result()

    def fill_bottle(self):
        """
        Fill the bottle by dispensing from multiple pumps in parallel.
        Uses multi-threading for parallel execution.
        """

        # Load sample data
        num_samples = self.sample_config["num_samples"]
        out_flow = self.sample_config["out_flow"]
        self.sample_id += 1

        if self.sample_id > num_samples:
            raise ValueError("Sample ID is out of range!")

        sample_info = self.sample_config["samples"][str(self.sample_id)]
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

                futures.append(
                    executor.submit(
                        self.hardware.execute_command,
                        "Pumps",
                        {"action": "dispense", "volume": sub_volume, "flow": sub_flow},
                        pump_id,
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

        # Step 1: Dip in the probe tip
        fb = self.hardware.execute_command("Arduino", {"action": "cylinder2 retract"})
        if fb != "Cylinder2 Retraction Finished":
            raise RequestFailed(
                "Cylinder_dls dip in request failed. Measurement cannot proceed."
            )

        # Step 2: Select the DLS measurement setup
        self.hardware.execute_command(
            "DLS", {"action": "select_measurement_setup", "id": setup_id}
        )

        # Step 3: Run the measurement and request data
        if self.hardware.execute_command(
            "DLS",
            {
                "action": "request_data",
                "num_of_runs": num_of_measure,
                "save_path": save_path,
            },
        ):
            # Retract the rod only if the measurement was successful
            return self.hardware.execute_command(
                "Arduino", {"action": "cylinder2 extend"}
            )

        return False

    def measure_UV(self, mode: str, save_path: str):
        # Step 1: Dark measurement (shutter closes)
        self.hardware.execute_command(
            "UV_Vis", {"action": "switch_shutter", "switch": True}
        )
        time.sleep(0.1)
        self.dark = self.hardware.execute_command("UV_Vis", {"action": "measure"})

        # Step 2: Reference measurement (shutter opens)
        self.hardware.execute_command(
            "UV_Vis", {"action": "switch_shutter", "switch": False}
        )
        time.sleep(0.1)
        self.refernce = self.hardware.execute_command("UV_Vis", {"action": "measure"})

        # Step 3: Dip the measure rod in the sample
        fb = self.hardware.execute_command("Arduino", {"action": "cylinder1 retract"})
        if fb != "Cylinder1 Retraction Finished":
            raise RequestFailed(
                "Cylinder_uvvis dip in request failed. Measurement cannot proceed."
            )

        # Step 4: Sample measurement
        self.sample = self.hardware.execute_command("UV_Vis", {"action": "measure"})

        # Step 5: Plot and save data

        # Step 5: Retract the probe rod
        return self.hardware.execute_command("Arduino", {"action": "cylinder1 extend"})

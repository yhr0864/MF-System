import time
import yaml
import json
import functools
from concurrent.futures import ThreadPoolExecutor

from devices.arduino import ArduinoBoard
from devices.gantry import Gantry
from devices.pump import SyringePump
from devices.dls import DLS_Analyzer
from devices.utils import RequestFailed, UnexpectedResponse, ErrorOccurred


class Hardware:
    def __init__(
        self,
        pump_config_path="./database/pump_config.yaml",
        sample_config_path="./database/sample_config.json",
    ):
        # self.gantry = Gantry()
        self.arduino = ArduinoBoard(port="COM14", baudrate=9600, timeout=0.1)
        # self.pump1 = SyringePump(
        #     pump_name="Nemesys_M_1_Pump",
        #     pressure_limit=10,
        #     inner_diameter_mm=14.70520755382068,
        #     max_piston_stroke_mm=60,
        # )
        # self.pump2 = SyringePump(
        #     pump_name="Nemesys_M_2_Pump",
        #     pressure_limit=10,
        #     inner_diameter_mm=14.70520755382068,
        #     max_piston_stroke_mm=60,
        # )
        # self.pump3 = SyringePump(
        #     pump_name="Nemesys_M_3_Pump",
        #     pressure_limit=10,
        #     inner_diameter_mm=32.80671055737278,
        #     max_piston_stroke_mm=60,
        # )
        # self.pump4 = SyringePump(
        #     pump_name="Nemesys_M_4_Pump",
        #     pressure_limit=10,
        #     inner_diameter_mm=32.80671055737278,
        #     max_piston_stroke_mm=60,
        # )
        # self.pump5 = SyringePump(
        #     pump_name="Nemesys_M_5_Pump",
        #     pressure_limit=10,
        #     inner_diameter_mm=23.207658393177034,
        #     max_piston_stroke_mm=60,
        # )
        # self.pump6 = SyringePump(
        #     pump_name="Nemesys_M_6_Pump",
        #     pressure_limit=10,
        #     inner_diameter_mm=23.207658393177034,
        #     max_piston_stroke_mm=60,
        # )
        # self.pump7 = SyringePump(
        #     pump_name="Nemesys_M_7_Pump",
        #     pressure_limit=10,
        #     inner_diameter_mm=23.207658393177034,
        #     max_piston_stroke_mm=60,
        # )
        # self.pump8 = SyringePump(
        #     pump_name="Nemesys_M_8_Pump",
        #     pressure_limit=10,
        #     inner_diameter_mm=10.40522314849599,
        #     max_piston_stroke_mm=60,
        # )

        self.dls = DLS_Analyzer(port="COM7", baudrate=9600, timeout=1)

        # self.pump6 = "Pump 6 is ready"
        # self.pump2 = "Pump 2 is ready"

        self.sample_id = 0

        # Read the config files for the experiment
        with open(pump_config_path, "r") as file:
            self.pump_config = yaml.safe_load(file)

        with open(sample_config_path, "r") as file:
            self.sample_data = json.load(file)

    def initialize(self):
        # self.gantry.initialize()
        self.arduino.initialize()
        time.sleep(1)
        print(self.home_table_p())
        print(self.home_table_m())
        print(self.home_probe_dls())
        print(self.home_probe_uv())

        # self.dls.initialize()
        # self.pump1.initialize()
        # self.pump2.initialize()
        # self.pump3.initialize()
        # self.pump4.initialize()
        # self.pump5.initialize()
        # self.pump6.initialize()
        # self.pump7.initialize()
        # self.pump8.initialize()
        # self.prepare_pump()

    def tray_to_pump(self, coord: tuple):
        coord_on_tray = coord[0]
        coord_on_table_p = coord[1]
        # self.gantry.move_from_to(coord_on_tray, coord_on_table_p)
        print("tray to pump")

    def pump_to_measure(self, coord: tuple):
        coord_on_table_p = coord[0]
        coord_on_table_m = coord[1]
        # self.gantry.move_from_to(coord_on_table_p, coord_on_table_m)
        print("pump to measure")

    def measure_to_tray(self, coord: tuple):
        coord_on_table_m = coord[0]
        coord_on_tray = coord[1]
        # self.gantry.move_from_to(coord_on_table_m, coord_on_tray)
        print("measure to tray")

    def home_table_p(self):
        return self.arduino.send_command("motor1 home")

    def home_table_m(self):
        return self.arduino.send_command("motor2 home")

    def rotate_table_p(self):
        return self.arduino.send_command("motor1 rotate")

    def rotate_table_m(self):
        return self.arduino.send_command("motor2 rotate")

    def home_probe_uv(self):
        return self.arduino.send_command("cylinder1 home")

    def home_probe_dls(self):
        return self.arduino.send_command("cylinder2 home")

    def dip_out_probe_uv(self):
        return self.arduino.send_command("cylinder1 extend")

    def dip_in_probe_uv(self):
        return self.arduino.send_command("cylinder1 retract")

    def dip_out_probe_dls(self):
        return self.arduino.send_command("cylinder2 extend")

    def dip_in_probe_dls(self):
        return self.arduino.send_command("cylinder2 retract")

    def prepare_pump(self):
        """
        Prepare the pumps before experiemnt => Refilling
        """

        # Refill all the pumps in the config files (Maybe NOT ALL)
        for key in self.pump_config.keys():
            pump = getattr(self, key)
            flow = self.pump_config[key]["flow"]

            if isinstance(pump, SyringePump):
                self.refill(pump=pump, flow=float(flow))

    def refill(self, pump: SyringePump, flow: float):
        pump.refill(flow)

    def empty(self, pump: SyringePump, flow: float):
        pump.empty(flow)

    def dose(self, pump: SyringePump, volume: float, flow: float):
        pump.dispense(volume, flow)

    def fill_bottle(self):
        # 1. Load sample data
        num_samples = self.sample_data["num_samples"]
        out_flow = self.sample_data["out_flow"]
        self.sample_id = self.sample_id + 1
        if self.sample_id > num_samples:
            raise ValueError("Sample ID is out of range!")

        sample_info = self.sample_data[str(self.sample_id)]

        volume = sample_info["volume"]
        proportion = sample_info["proportion"]
        solution = sample_info["solution"]
        pumps = sample_info["pumps"]

        # Parallelly dispensing with multi-threading
        with ThreadPoolExecutor() as executor:
            futures = []
            for i in range(len(proportion)):
                ratio = proportion[i] / sum(proportion)
                sub_flow = out_flow * ratio
                sub_volume = volume * ratio
                p = pumps[i]
                # print(ratio)
                # print(sub_flow)
                # print(sub_volume)
                # print(p)
                pump = getattr(self, p)
                if isinstance(pump, SyringePump):
                    futures.append(
                        executor.submit(
                            self.dose(
                                pump=pump,
                                volume=float(sub_volume),
                                flow=float(sub_flow),
                            )
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
    hardware = Hardware()
    print("start init")
    hardware.initialize()
    print("finish init")
    # hardware.prepare_pump()
    # hardware.fill_bottle()

    f = hardware.measure_DLS(
        setup_id=5, num_of_measure=3, save_path="./database/measurement_dls.csv"
    )

    f.result()

import time
import numpy as np
import matplotlib.pyplot as plt

from mf_system.hardware.devices.utils import DeviceNotFoundError
from mf_system.hardware.devices.interface import IHardwareAdapter
from mf_system.hardware.devices.uv_vis_lib.uvvissdk import uvvisremotecontrol

# Types of FLEX devices
FLEX_types = ["STD", "RES+"]


class UVvisAdapter(IHardwareAdapter):
    def __init__(self, config: dict):
        self.device_id = None
        self.FTHandle_ID = None
        self._connection = None
        self.int_time = config["integration_time"]
        self.average = config["average"]
        self.smoothing = config["smoothing"]

    def initialize(self):
        self._connection = uvvisremotecontrol.UVvis()
        device_info = self._connection.scan_devices()
        n_devices = device_info[0]  # Index 0 contains the number of connected devices

        if n_devices == 0:
            raise DeviceNotFoundError("No devices found!")

        self.device_id = device_info[1]
        print(
            f"Current device {self.device_id} with serial number: {self._connection.get_serial(self.device_id)}"
        )

        FLEX_type_n = device_info[2]

        print(f"Device type: {FLEX_types[FLEX_type_n]}")

        # Connects and gets handle to use with other functions
        self.FThandle_ID = self._connection.connect(self.device_id)

        # Disable trigger in/out mode
        self._connection.trigger_in_disable(self.FThandle_ID)
        self._connection.trigger_out_on_off(False, self.FThandle_ID)

        if self.FThandle_ID != -1:  # Test if the connection was successful
            self._connection.switch_LED(True, self.FThandle_ID)  # Turn the LED on

    def execute(self, command: dict) -> str:
        action = command["action"]

        match action:
            case "change_integration_time":
                return self._connection.change_integration_time(
                    command["int_time"], self.FTHandle_ID
                )
            case "measure":
                return self.measure()
            case "switch_LED":
                return self._connection.switch_LED(command["switch"], self.FTHandle_ID)
            case "switch_shutter":
                return self._connection.switch_shutter(
                    command["switch"], self.FTHandle_ID
                )
            case _:
                raise ValueError(f"Unsupported command: {action}")

    def shutdown(self) -> None:
        if self._connection:
            self._connection.disconnect(self.FThandle_ID)

    def measure(self):
        self._connection.change_integration_time(self.int_time, self.FThandle_ID)

        # Get wavelenth array (list type)
        c0, c1, c2, c3 = self._connection.read_EEPROMCoeff(self.FThandle_ID)
        wavelengths = self._connection.get_XData(c0, c1, c2, c3, self.FThandle_ID)
        n_pixels = len(wavelengths)

        return self._connection.get_YData(False, self.FThandle_ID)[:n_pixels]

    def get_Absorbance(self, Sn: list, Dn: list, Rn: list):
        An = -np.log10((Sn - Dn) / (Rn - Dn))
        return An

    def get_Transmittance(self, Sn: list, Dn: list, Rn: list):
        Tn = (Sn - Dn) / (Rn - Dn) * 100
        return Tn

    def plot_result(self, wavelengths, spectrum, save_path):
        plt.subplots()
        plt.plot(wavelengths, spectrum)
        plt.xlabel(r"$\lambda$ (nm)")
        plt.ylabel("Intensity (counts)")
        plt.xlim(wavelengths[0], wavelengths[-1])
        plt.ylim(
            np.min(spectrum) - 0.05 * (np.max(spectrum) - np.min(spectrum)),
            np.max(spectrum) + 0.05 * (np.max(spectrum) - np.min(spectrum)),
        )

        # Save the plot
        plt.savefig(save_path)
        plt.show()


if __name__ == "__main__":
    uvvis = UVvisAdapter({"device_id": 0})
    uvvis.initialize()

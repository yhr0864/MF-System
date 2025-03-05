import time
import numpy as np
import matplotlib.pyplot as plt

from mf_system.hardware.devices.utils import DeviceNotFoundError, moving_average
from mf_system.hardware.devices.interface import IHardwareAdapter
from mf_system.hardware.devices.uv_vis_lib.uvvissdk import uvvisremotecontrol

# Types of FLEX devices
FLEX_types = ["STD", "RES+"]


class UVvisAdapter(IHardwareAdapter):
    def __init__(self, config: dict):
        self.FTHandle_ID = None
        self._connection = None
        self.int_time = config["integration_time"]
        self.average = config["average"]
        self.smoothing = config["smoothing"]

    def initialize(self):
        self._connection = uvvisremotecontrol.UVvis()
        device_info = self._connection.scan_devices()
        print(device_info)
        n_devices = device_info[0]  # Index 0 contains the number of connected devices

        if n_devices == 0:
            raise DeviceNotFoundError("No devices found!")

        device_id = device_info[1]
        print(
            f"Current device {device_id} with serial number: {self._connection.get_serial(device_id)}"
        )

        FLEX_type_n = device_info[2]

        print(f"Device type: {FLEX_types[FLEX_type_n]}")

        # Connects and gets handle to use with other functions
        self.FTHandle_ID = self._connection.connect(device_id)

        # Disable trigger in/out mode
        self._connection.trigger_in_disable(self.FTHandle_ID)
        self._connection.trigger_out_on_off(False, self.FTHandle_ID)

        if self.FTHandle_ID != -1:  # Test if the connection was successful
            self._connection.switch_LED(True, self.FTHandle_ID)  # Turn the LED on

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
            self._connection.disconnect(self.FTHandle_ID)

    def measure(self):
        self._connection.change_integration_time(self.int_time, self.FTHandle_ID)

        # Get wavelenth array (list type)
        c0, c1, c2, c3 = self._connection.read_EEPROMCoeff(self.FTHandle_ID)
        wavelengths = self._connection.get_XData(c0, c1, c2, c3, self.FTHandle_ID)
        n_pixels = len(wavelengths)

        # Averaging
        res_list = []
        for i in range(self.average):
            res_list.append(
                self._connection.get_YData(False, self.FTHandle_ID)[:n_pixels]
            )

        data = np.array(res_list)
        mean_values = np.mean(data, axis=0)

        # Smoothing
        if self.smoothing > 1:
            mean_values = moving_average(mean_values, window_size=self.smoothing)

        return wavelengths, mean_values

    def get_Absorbance(self, Sn: list[float], Dn: list[float], Rn: list[float]):
        An = -np.log10((Sn - Dn) / (Rn - Dn))
        return An

    def get_Transmittance(self, Sn: list[float], Dn: list[float], Rn: list[float]):
        Tn = (Sn - Dn) / (Rn - Dn) * 100
        return Tn

    def plot_result(self, wavelengths, spectrum, save_path):
        plt.subplots()
        plt.plot(wavelengths, spectrum)
        plt.xlabel(r"Wavelength (nm)")
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
    uvvis = UVvisAdapter({"integration_time": 1000, "average": 5, "smoothing": 11})
    uvvis.initialize()
    uvvis.execute({"action": "switch_shutter", "switch": True})
    time.sleep(0.1)
    wave_d, dark = uvvis.measure()
    uvvis.execute({"action": "switch_shutter", "switch": False})
    time.sleep(0.1)
    wave_r, ref = uvvis.measure()
    print("ref finished, please dip the probe in the sample")
    time.sleep(5)

    wave_s, sample = uvvis.measure()

    An = uvvis.get_Absorbance(sample, dark, ref)

    uvvis.plot_result(wave_d, dark, "./plot_dark.png")
    uvvis.plot_result(wave_r, ref, "./plot_ref.png")
    uvvis.plot_result(wave_s, An, "./plot_sample.png")
    time.sleep(0.1)

    uvvis.shutdown()

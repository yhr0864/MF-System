from mf_system.hardware.devices.utils import DeviceNotFoundError
from mf_system.hardware.devices.interface import IHardwareAdapter
from mf_system.hardware.devices.uv_vis_lib.uvvissdk import uvvisremotecontrol

# Types of FLEX devices
FLEX_types = ["STD", "RES+"]


class UVvisAdapter(IHardwareAdapter):
    def __init__(self, config: dict):
        self._connection = None
        self.id = config["device_id"]

    def initialize(self):
        self._connection = uvvisremotecontrol.UVvis()

        # Step 1: Get information of connected FLEX devices
        device_info = self._connection.scan_devices()
        n_devices = device_info[0]  # Index 0 contains the number of connected devices

        if n_devices == 0:
            raise DeviceNotFoundError("No devices found!")
        else:
            print(f"Totally {n_devices} devices found")
            print(
                f"Current device {self.id} with serial number: {self._connection.get_serial(self.id)}"
            )

            # Even natural indexes contain the number corresponding to the type of FLEX device
            FLEX_type_n = device_info[2 * (self.id + 1)]

            print(f"Device type: {FLEX_types[FLEX_type_n]}")

            # Connects and gets handle to use with other functions
            FThandle_ID = self._connection.connect(self.id)

            if FThandle_ID != -1:  # Test if the connection was successful
                self._connection.switch_LED(True, FThandle_ID)  # Turn the LED on

                # Change integration time to the lowest value possible
                if FLEX_type_n == 0:
                    integration_time = 2
                else:
                    integration_time = 3
                self._connection.change_integration_time(integration_time, FThandle_ID)

                # Get wavelenth array (list type)
                c0, c1, c2, c3 = self._connection.read_EEPROMCoeff(FThandle_ID)
                wavelengths = self._connection.get_XData(c0, c1, c2, c3, FThandle_ID)
                n_pixels = len(wavelengths)
                print(n_pixels)

    def execute(self, command: dict) -> str:
        action = command["action"]

        match action:
            case "connect":
                return self._connection.connect(self.id)
            case "disconnect":
                return self._connection.disconnect(self.id)
            case "scan_devices":
                return self._connection.scan_devices()
            case "get_serial":
                return self._connection.get_serial(self.id)
            case "change_integration_time":
                return self._connection.change_integration_time(
                    command["int_time"], self.id
                )
            case "get_YData":
                return self._connection.get_YData(command["external_trigger"], self.id)
            case "get_XData":
                return self._connection.get_XData(
                    command["c0"],
                    command["c1"],
                    command["c2"],
                    command["c3"],
                    self.id,
                )
            case "switch_LED":
                return self._connection.switch_LED(command["switch"], self.id)
            case "read_EEPROMCoeff":
                return self._connection.read_EEPROMCoeff(self.id)
            case "switch_shutter":
                return self._connection.switch_shutter(self.id)
            case "trigger_in_disable":
                return self._connection.trigger_in_disable(self.id)
            case "trigger_in_enable":
                return self._connection.trigger_in_enable(
                    command["trigger_in_delay"], self.id
                )
            case "trigger_out_on_off":
                return self._connection.trigger_out_on_off(command["switch"], self.id)
            case "prepare_SpecACK":
                return self._connection.prepare_SpecACK(self.id)
            case _:
                raise ValueError(f"Unsupported command: {action}")

    def shutdown(self) -> None:
        if self._connection:
            self._connection.disconnect(self.id)


if __name__ == "__main__":
    uvvis = UVvisAdapter({"device_id": 0})
    uvvis.initialize()

import os
import time

from mf_system.hardware.devices.interface import IHardwareAdapter
from mf_system.hardware.devices.pump_lib.qmixsdk import qmixbus, qmixpump, qmixanalogio


class SyringePumpAdapter(IHardwareAdapter):
    _bus_opened = False

    def __init__(self, config: dict):
        super().__init__()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.deviceconfig = os.path.join(script_dir, "pump_lib/PumpConfig")
        self.pump_name = config["name"]
        self.__pressure_limit = config["pressure_limit"]
        self.__inner_diameter_mm = config["inner_diameter_mm"]
        self.__max_piston_stroke_mm = config["max_piston_stroke_mm"]

    @staticmethod
    def connect(deviceconfig):
        print("Opening bus with deviceconfig ", deviceconfig)
        bus = qmixbus.Bus()
        bus.open(deviceconfig, "")
        __class__._bus_opened = True
        print("Starting bus communication...")
        bus.start()

    def initialize(self) -> bool:
        """
        Initialize the pump
        """

        try:
            # Step 1. Connect to pumps controller
            # Make sure bus only opened once
            if not self._bus_opened:
                SyringePumpAdapter.connect()

            # Step 2. Create pump
            self.pump = qmixpump.Pump()
            self.pump.lookup_by_name(self.pump_name)
            # self.pump_name = self.pump.get_device_name()

            # Step 3. Enable the pump
            # If pump is in fault state, clear it
            if self.pump.is_in_fault_state():
                self.pump.clear_fault()

            if not self.pump.is_enabled():
                self.pump.enable(True)

            # Step 4. Set syringe parameters
            self.pump.set_syringe_param(
                self.__inner_diameter_mm, self.__max_piston_stroke_mm
            )

            # Step 5. Initialize valves
            if not self.pump.has_valve():
                raise ModuleNotFoundError("no valve installed")
            self.valve = self.pump.get_valve()
            self.switch_valve_to(0)

            # Step 6. Initialize pressure sensor
            self.pressure_channel = qmixanalogio.AnalogInChannel()
            self.pressure_channel.lookup_channel_by_name(f"{self.pump_name[:-5]}_AnIN1")
            self.current_pressure_sensor_status = self.pressure_channel.read_status()
            self.pressure_channel.enable_software_scaling(True)
            self.pressure_channel.set_scaling_param(0.05, -25)
            print(f"Current sensor status: {self.current_pressure_sensor_status}")
            print(
                f"Current scaling factors: {self.pressure_channel.get_scaling_param()}"
            )

            # Step 5. Setup the unit (milli/s by default)
            self.set_units(
                unit_prefix=qmixpump.UnitPrefix.milli,
                time_unit=qmixpump.TimeUnit.per_second,
            )
        except ConnectionError:
            return False

    def execute(self, command: dict) -> str:
        if command["action"] == "aspirate":
            return self.aspirate(command["volume"], command["flow"])
        elif command["action"] == "dispense":
            return self.dispense(command["volume"], command["flow"])
        elif command["action"] == "refill":
            return self.refill(command["flow"])
        elif command["action"] == "empty":
            return self.empty(command["flow"])
        elif command["action"] == "stop_pump":
            return self.stop_pump()

    def shutdown(self) -> None:
        SyringePumpAdapter.stop_all_pumps()
        self.capi_close()

    def wait_dosage_finished(self, timeout_seconds):
        """
        The function waits until the last dosage command has finished
        until the timeout occurs.
        """

        timer = qmixbus.PollingTimer(timeout_seconds * 1000)
        message_timer = qmixbus.PollingTimer(500)
        result = True
        while result:
            if timer.is_expired():
                raise TimeoutError("Timeout!")
            # Monitor the force if it is below the threshold
            current_pressure = self.pressure_channel.read_input()
            if current_pressure >= self.__pressure_limit:
                print(
                    f"Warning: Current pressure {current_pressure} is over the limit. Pump stops!"
                )
                self.pump.stop_pumping()
                break

            time.sleep(0.1)
            if message_timer.is_expired():
                print(
                    f"{self.pump_name} - Dosed vol.: {self.pump.get_dosed_volume():.6f}, Flow rate: {self.pump.get_flow_is():.6f}, Fill level: {self.pump.get_fill_level():.6f}, Current pressure: {current_pressure:.2f}"
                )
                message_timer.restart()

            result = self.pump.is_pumping()
        return not result

    def set_units(self, unit_prefix, time_unit):
        """
        Setup the unit for volume and flow rate
        """

        self.pump.set_volume_unit(unit_prefix, qmixpump.VolumeUnit.litres)
        max_vol = self.pump.get_volume_max()
        print(f"Max. volume: {max_vol} {self.pump.get_volume_unit()}")

        self.pump.set_flow_unit(unit_prefix, qmixpump.VolumeUnit.litres, time_unit)
        max_flow = self.pump.get_flow_rate_max()
        print(f"Max. flow: {max_flow} {self.pump.get_flow_unit()}")

    def aspirate(self, volume, flow, timeout=600):
        """
        Aspirate a certain volume with a certain flow rate.
        """

        self.switch_valve_to(1)
        self.pump.aspirate(volume, flow)

        isFinished = self.wait_dosage_finished(timeout)
        self.switch_valve_to(0)
        return isFinished

    def dispense(self, volume, flow, timeout=600):
        """
        Dispense a certain volume with a certain flow rate.
        """

        self.switch_valve_to(2)
        self.pump.dispense(volume, flow)
        isFinished = self.wait_dosage_finished(timeout)
        self.switch_valve_to(0)
        return isFinished

    def refill(self, flow, timeout=1200):
        """
        Refill the syringe with a certain flow rate.
        """

        self.switch_valve_to(1)
        flow = 0 - flow
        isFinished = self.generate_flow(flow, timeout)
        self.switch_valve_to(0)
        return isFinished

    def empty(self, flow, timeout=1200):
        """
        Empty the syringe with a certain flow rate.
        """

        self.switch_valve_to(2)
        isFinished = self.generate_flow(flow, timeout)
        self.switch_valve_to(0)
        return isFinished

    def generate_flow(self, flow, timeout):
        """
        Generate a continuous flow.

        A negative flow indicates aspiration and a positiove flow indicates
        dispension.
        """

        self.pump.generate_flow(flow)
        isFinished = self.wait_dosage_finished(timeout)
        return isFinished

    def switch_valve_to(self, position: int):
        """
        Switch the valve to a certain position.

        0: Close, 1: Aspirate, 2: Dispense
        """

        self.valve.switch_valve_to_position(position)
        time.sleep(0.5)  # give valve some time to move to target

        # Ensure the valve is in the right position
        valve_pos_is = self.valve.actual_valve_position()
        if not (valve_pos_is == position):
            raise RuntimeError("Valve failed to be switched")

    def stop_pump(self):
        """
        Immediately stop pumping.
        """

        self.pump.stop_pumping()

    @staticmethod
    def stop_all_pumps():
        """
        Immediately stop pumping off all pumps.
        """
        qmixpump.Pump.stop_all_pumps()

    def capi_close(self):
        """
        Close bus communication.
        """

        # Make sure bus only closed once
        if self._bus_opened:
            print("Closing bus...")
            self.bus.stop()
            self.bus.close()
            self.__class__._bus_opened = True
            print("Bus closed")
        else:
            print("Bus closed")

if __name__ == "__main__":

    pump1 = SyringePumpAdapter("Nemesys_M_1_Pump", 10, 14.70520755382068, 60)
    pump2 = SyringePumpAdapter("Nemesys_M_2_Pump", 10, 14.70520755382068, 60)
    pump3 = SyringePumpAdapter("Nemesys_M_3_Pump", 10, 32.80671055737278, 60)
    pump4 = SyringePumpAdapter("Nemesys_M_4_Pump", 10, 32.80671055737278, 60)
    pump5 = SyringePumpAdapter("Nemesys_M_5_Pump", 10, 23.207658393177034, 60)
    pump6 = SyringePumpAdapter("Nemesys_M_6_Pump", 10, 23.207658393177034, 60)
    pump7 = SyringePumpAdapter("Nemesys_M_7_Pump", 10, 23.207658393177034, 60)
    pump8 = SyringePumpAdapter("Nemesys_M_8_Pump", 10, 10.40522314849599, 60)

    # test(pump6)

    multi_thread_test(pump6)
    time.sleep(0.01)
    multi_thread_test(pump2)
    # # time.sleep(0.001)
    # multi_thread_test(pump7)

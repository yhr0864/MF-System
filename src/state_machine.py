import sys
import time
import logging
from concurrent.futures import ThreadPoolExecutor

from transitions_gui import WebMachine

from hardware import Hardware
from utils import states, transitions


class StateMachine:
    def __init__(self) -> None:
        self.machine = WebMachine(
            model=self,
            states=states,
            transitions=transitions,
            initial="initialize",
            name="Micro Fluidic System",
            ignore_invalid_triggers=True,
            auto_transitions=False,
            port=8083,
        )

        self.hardware = Hardware()
        self.feedback = None
        # Simulate 3 bottles
        self.cnt = 3
        self.is_bottle_on_tray = True

    def initialize(self):
        # Initialize all the hardwares
        self.hardware.initialize()
        time.sleep(1)

        # transition
        self.trigger("initialize_finished")

    def before_cycle_stage_1(self):
        # Send command
        # self.hardware.tray_to_pump()
        time.sleep(2)

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_2(self):
        # Send command
        self.feedback = self.hardware.rotate_table_p()
        time.sleep(1)

        if self.feedback:
            self.feedback = None
            # transition
            self.trigger("command_finished")

    def before_cycle_stage_3(self):
        # Send command
        # with ThreadPoolExecutor() as executor:
        #     future1 = executor.submit(self.hardware.fill_bottle())
        #     future2 = executor.submit(self.hardware.tray_to_pump())

        #     future1.result()
        #     future2.result()

        time.sleep(1)

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_4(self):
        # Send command
        self.feedback = self.hardware.rotate_table_p()
        time.sleep(1)

        if self.feedback:
            self.feedback = None
            # transition
            self.trigger("command_finished")

    def before_cycle_stage_5(self):
        # Send command
        # with ThreadPoolExecutor() as executor:
        #     future1 = executor.submit(self.hardware.fill_bottle())
        #     future2 = executor.submit(self.hardware.pump_to_measure())

        #     future1.result()
        #     future2.result()

        time.sleep(1)

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_6(self):
        # Send command
        self.feedback = self.hardware.rotate_table_m()
        time.sleep(1)

        if self.feedback:
            self.feedback = None
            # transition
            self.trigger("command_finished")

    def before_cycle_stage_7(self):
        # Send command
        # with ThreadPoolExecutor() as executor:
        #     future1 = executor.submit(self.hardware.tray_to_pump())
        #     future2 = executor.submit(self.hardware.measure_UV())

        #     future1.result()
        #     future2.result()

        time.sleep(1)

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_8(self):
        # Send command
        self.feedback = self.hardware.rotate_table_p()
        time.sleep(1)

        if self.feedback:
            self.feedback = None
            # transition
            self.trigger("command_finished")

    def before_cycle_stage_9(self):
        # Send command
        # with ThreadPoolExecutor() as executor:
        #     future1 = executor.submit(self.hardware.fill_bottle())
        #     future2 = executor.submit(self.hardware.pump_to_measure())

        #     future1.result()
        #     future2.result()

        time.sleep(1)

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_10(self):
        # Send command
        self.feedback = self.hardware.rotate_table_m()
        time.sleep(1)

        if self.feedback:
            self.feedback = None

            # transition
            self.trigger("command_finished")

    def before_cycle_stage_11(self):
        # Send command
        # self.hardware.tray_to_pump()
        time.sleep(1)

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_12(self):
        # Send command
        self.feedback = self.hardware.rotate_table_p()
        time.sleep(1)

        if self.feedback:
            self.feedback = None
            # transition
            self.trigger("command_finished")

    def before_cycle_stage_13(self):
        # Send command
        # with ThreadPoolExecutor() as executor:
        #     future1 = executor.submit(self.hardware.fill_bottle())
        #     future2 = executor.submit(self.hardware.pump_to_measure())
        #     future3 = executor.submit(self.hardware.measure_DLS())
        #     future4 = executor.submit(self.hardware.measure_UV())

        #     future1.result()
        #     future2.result()
        #     future3.result()
        #     future4.result()

        time.sleep(1)

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_14(self):
        # Send command
        self.feedback = self.hardware.rotate_table_m()
        time.sleep(1)

        if self.feedback:
            self.feedback = None
            # transition
            self.trigger("command_finished")

    def before_cycle_stage_15(self):
        # Send command
        # self.hardware.tray_to_pump()
        time.sleep(1)

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_16(self):
        # Send command
        self.feedback = self.hardware.rotate_table_p()
        time.sleep(1)

        if self.feedback:
            self.feedback = None
            # transition
            self.trigger("command_finished")

    def before_cycle_stage_17(self):
        # Send command
        # with ThreadPoolExecutor() as executor:
        #     future1 = executor.submit(self.hardware.fill_bottle())
        #     future2 = executor.submit(self.hardware.measure_DLS())
        #     future3 = executor.submit(self.hardware.measure_UV())

        #     future1.result()
        #     future2.result()
        #     future3.result()

        time.sleep(1)

        # transition
        self.trigger("command_finished")

    ############################

    def cycle_stage_1(self):
        # Send command
        # self.hardware.measure_to_tray()
        time.sleep(1)

        # transition
        self.trigger("command_finished")

    def cycle_stage_2(self):
        # Send command
        # self.hardware.pump_to_measure()
        time.sleep(1)

        # transition
        self.trigger("command_finished")

    def cycle_stage_3(self):
        # Send command
        self.feedback = self.hardware.rotate_table_m()
        time.sleep(1)

        if self.feedback:
            self.feedback = None
            # transition
            self.trigger("command_finished")

    def cycle_stage_4(self):
        # Send command
        # with ThreadPoolExecutor() as executor:
        #     future1 = executor.submit(self.hardware.measure_DLS())
        #     future2 = executor.submit(self.hardware.measure_UV())

        #     future1.result()
        #     future2.result()
        if self.cnt == 0:
            self.is_bottle_on_tray = False

        self.cnt -= 1

        time.sleep(1)

        # transition
        self.trigger("command_finished")

    def cycle_stage_branch(self):
        # Send command
        # self.hardware.tray_to_pump()
        time.sleep(1)

        # transition
        self.trigger("command_finished")

    def cycle_stage_6(self):
        # Send command
        self.feedback = self.hardware.rotate_table_p()
        time.sleep(1)

        if self.feedback:
            self.feedback = None
            # transition
            self.trigger("command_finished")

    def cycle_stage_7(self):
        # Send command
        # self.hardware.fill_bottle()
        time.sleep(1)

        # transition
        self.trigger("command_finished")

    ########################################

    def after_cycle_stage(self):
        # Send command
        self.feedback = self.hardware.rotate_table_p()
        time.sleep(1)

        if self.feedback:
            self.feedback = None
            # transition
            self.trigger("command_finished")

    def after_cycle_stage_2(self):
        # Send command
        # self.hardware.measure_to_tray()
        time.sleep(1)

        # transition
        self.trigger("command_finished")

    def after_cycle_stage_3(self):
        # Send command
        # self.hardware.pump_to_measure()
        time.sleep(1)

        # transition
        self.trigger("command_finished")

    def after_cycle_stage_4(self):
        # Send command
        self.feedback = self.hardware.rotate_table_m()
        time.sleep(1)

        if self.feedback:
            self.feedback = None
            # transition
            self.trigger("command_finished")

    def after_cycle_stage_5(self):
        # Send command
        # with ThreadPoolExecutor() as executor:
        #     future1 = executor.submit(self.hardware.measure_DLS())
        #     future2 = executor.submit(self.hardware.measure_UV())
        #     future3 = executor.submit(self.hardware.measure_to_tray())

        #     future1.result()
        #     future2.result()
        #     future3.result()

        time.sleep(1)

        # transition
        self.trigger("command_finished")

    def after_cycle_stage_6(self):
        # Send command
        self.feedback = self.hardware.rotate_table_m()
        time.sleep(1)

        if self.feedback:
            self.feedback = None
            # transition
            self.trigger("command_finished")

    def after_cycle_stage_7(self):
        # Send command
        # with ThreadPoolExecutor() as executor:
        #     future1 = executor.submit(self.hardware.measure_DLS())
        #     future2 = executor.submit(self.hardware.measure_to_tray())

        #     future1.result()
        #     future2.result()

        time.sleep(1)

        # transition
        self.trigger("command_finished")

    def after_cycle_stage_8(self):
        # Send command
        self.feedback = self.hardware.rotate_table_m()
        time.sleep(1)

        if self.feedback:
            self.feedback = None
            # transition
            self.trigger("command_finished")

    def after_cycle_stage_9(self):
        # Send command
        # self.hardware.measure_to_tray()
        time.sleep(1)

        # transition: last state finished => end the server
        self.machine.stop_server()
        sys.exit()

    def auto_run(self):
        while True:
            action = getattr(self, self.state, lambda: "No action for this state")
            if action:
                action()
            time.sleep(2)


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Create the table state machine
    table = StateMachine()

    try:
        # Start automatic state transitions
        table.auto_run()

    except KeyboardInterrupt:
        logging.info("Stopping the server...")
        table.machine.stop_server()
